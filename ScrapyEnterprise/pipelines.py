# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from datetime import datetime
from typing import Optional, Tuple
import hashlib
import pymongo
import pymongo.errors
import pytz
import requests
from kombu import Connection, Producer
from kombu.pools import producers
from scrapy.exceptions import DropItem
from policy_crawler.items import PolicyItem


class HashItem(object):
    """对数据做hash处理"""
    def __init__(self, url, title, content):
        self.url_hash = self.hash_url(url)
        self.title_hash = self.hash_title(title)
        self.content_hash = self.hash_content(content)

    @staticmethod
    def hash(value: str):
        return hashlib.sha1(value.encode('utf8')).hexdigest()

    @staticmethod
    def hash_url(url):
        # url去掉协议和后缀斜杠后hash
        url = url.rstrip('/')
        url = re.sub(r'^https?://', '', url, 1)
        return HashItem.hash(url)

    @staticmethod
    def hash_title(title):
        # 标题去掉非文字部分后hash
        title = re.sub(r'\W', '', title)
        return HashItem.hash(title)

    @staticmethod
    def hash_content(content):
        # 正文选择去最长的3句作为特征进行hash
        parts = content.split()
        sentences = []
        for part in parts:
            part_ = re.split(r'。|？|！|；|……|\?|!|;|\.\.\.', part)
            sentences.extend(part_)
        sentences.sort(key=len, reverse=True)
        sentences_k3 = sentences[:3]
        if any([len(i) < 20 for i in sentences_k3]):
            # 内容太短无法作为特征
            return None
        feature = re.sub(r'\W', '', ''.join(sentences_k3))
        return HashItem.hash(feature)



class ProcessPipeline(object):
    """post-process"""

    def __init__(self):
        # self.url = api_url
        self.session: Optional[requests.Session] = None

    def open_spider(self, spider):
        self.session = requests.Session()

    def process_item(self, item: PolicyItem, spider):
        item.update(item)
        return item

    def close_spider(self, spider):
        self.session.close()



class PersistPipeline(object):
    """保存item到MongoDB"""
    def __init__(self, mongo_uri, mongo_db, amqp_url, amqp_queue):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        self.col = None
        self.amqp_url = amqp_url
        self.amqp_queue = amqp_queue
        self.broker: Optional[Connection] = None
        self.producer: Optional[Producer] = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            amqp_url=crawler.settings.get('AMQP_URL'),
            amqp_queue=crawler.settings.get('AMQP_QUEUE'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.col = self.db[spider.collection]
        self.check_index()
        self.broker = Connection(self.amqp_url)
        self.producer = producers[self.broker].acquire(block=True, timeout=10)

    def check_index(self):
        """创建索引"""
        indexes = self.col.index_information().keys()
        for f in ['detailUrl', 'url_f', 'content_f']:
            if f in indexes:
                continue
            self.col.create_index(
                [(f, 1)], name=f, unique=True,
                partialFilterExpression={f: {'$type': 'string'}}
            )

    def process_item(self, item: PolicyItem, spider):
        data = item.to_dict()
        job = getattr(spider, '_job', None)
        data['task_id'] = job
        oid = self.to_mongo(data)
        if job:
            # 开发环境不推送消息
            item['id'] = f'{oid}@{spider.collection}'
            self.to_mq(item)
            self.col.update_one(
                {'_id': oid}, {'$set': {'sent': True}}
            )
        return item

    def to_mongo(self, data):
        feature = HashItem(
            data['detailUrl'], data['title'], data['plain_text']
        )
        data['url_f'] = feature.url_hash
        if feature.title_hash and feature.content_hash:
            data['content_f'] = feature.title_hash + feature.content_hash
        else:
            data['content_f'] = None
        data['insert_time'] = datetime.now(tz=pytz.UTC)
        data['sent'] = False  # 发送至消息队列
        try:
            cursor = self.col.insert_one(data)
        except pymongo.errors.DuplicateKeyError as e:
            raise DropItem(f'{e.args[0]}')
        return cursor.inserted_id

    def to_mq(self, item):
        self.producer.publish(
            item.to_json(),
            routing_key=self.amqp_queue,
            content_type='text/plain'
        )

    def close_spider(self, spider):
        self.client.close()
        self.broker.close()
        self.producer.release()



class AMQPPipeline(object):
    """发送item到rabbitmq"""
    def __init__(self, amqp_url, amqp_queue):
        self.amqp_url = amqp_url
        self.amqp_queue = amqp_queue
        self.broker: Optional[Connection] = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            amqp_url=crawler.settings.get('AMQP_URL'),
            amqp_queue=crawler.settings.get('AMQP_QUEUE'),
        )

    def open_spider(self, spider):
        self.broker = Connection(self.amqp_url)

    def process_item(self, item: PolicyItem, spider):
        with producers[self.broker].acquire(block=True) as producer:
            producer.publish(
                item.to_json(),
                routing_key=self.amqp_queue,
                content_type='text/plain'
            )
        return item

    def close_spider(self, spider):
        self.broker.close()



