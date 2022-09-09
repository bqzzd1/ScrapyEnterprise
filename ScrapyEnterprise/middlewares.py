# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from queue import Queue
from urllib.parse import urljoin
import requests
from scrapy import signals, Request,FormRequest
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import re
from pathlib import Path
from twisted.internet.error import TimeoutError
from scrapy import signals
from scrapy.spidermiddlewares.httperror import HttpError
import pymongo
import pymongo.errors
from scrapy.exceptions import DropItem
# from itemadapter import is_item, ItemAdapter
from scrapy.utils.project import get_project_settings




class PolicyCrawlerSpiderMiddleware():
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def __init__(self):
        project_settings = get_project_settings()
        self.items_scraped = 0
        self.filt_api = project_settings['FILT_API']
        self.app_api = project_settings['APP_API']
        self.app_token = project_settings['APP_TOKEN']
        self.crawl_page = project_settings['CRAWL_PAGE']
        self.mongo_uri = project_settings['MONGO_URI']
        self.mongo_db = project_settings['MONGO_DB']
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.item_scraped, signal=signals.item_scraped)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        # Should return None or raise an exception.
        return None

    def filter_policy(self,title: str) -> int:
        """
        使用关键词、正则规则对政策进行初步过滤
        初步排除非目标数据减轻
        Arguments:
            title (str): 政策标题
        Return:
            是否政策. 1: 可能是政策，需要后续分类判断，不排除; 0: 确定为非政策，排除
        """
        BASE_DIR = Path(__file__).parent
        filter_words = (BASE_DIR / 'public' / 'filter_words.txt').read_text(encoding='utf-8').split()
        filter_patterns = (BASE_DIR / 'public' / 'filter_patterns.txt').read_text(encoding='utf-8').split()

        for w in filter_words:
            if w in title:
                return 0
        for p in filter_patterns:
            if re.search(p, title):
                return 0
        return 1

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        # Must return an iterable of Request, or item objects.

        for i in result:
            if isinstance(i, Request) or isinstance(i, FormRequest):
                # 爬取指定的页数
                if self.crawl_page > 0 and i.meta.__contains__('page'):
                    page = i.meta['page']
                    if page > self.crawl_page:
                        print('只爬取指定页')
                        continue
                # 过略无关项
                # if isinstance(i.cb_kwargs, dict) and 'title' in i.cb_kwargs:
                #     title = i.cb_kwargs['title']
                #     keep = self.filter_policy(title)
                #     # keep = requests.post(
                #     #     self.filt_api, json={'title': title}).json()
                #     if not keep:
                #         spider.logger.warning(f'skipped: {title} {i.url}')
                #         continue
            yield i
    def process_spider_exception(self,response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.
        # Should return either None or an iterable of Request or item objects.
        return None


    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.
        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        job = getattr(spider, '_job', None)
        if job:
            url = urljoin(self.app_api, 'schedule/')
            requests.post(url, json={
                'spider_name': spider.name,
                'website_name': spider.website_name,
                'website_url': spider.website_url,
                'mongo_db_name': 'policy_data',
                'mongo_col_name': spider.collection,
                'task_id': job
            }, headers={'Authorization': f'Token {self.app_token}'})

    def spider_closed(self, spider):
        job = getattr(spider, '_job', None)
        if job:
            url = urljoin(self.app_api, f'finish/{job}/')
            requests.put(url, json={
                'data_count': self.items_scraped,
            }, headers={'Authorization': f'Token {self.app_token}'})

    def item_scraped(self, item, spider):
        self.items_scraped += 1



class RotateUserAgentMiddleware(UserAgentMiddleware):
    __user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.__user_agent_list)
        if ua:
            request.headers['User-Agent']=ua


class ProxyDownloaderMiddleware(RetryMiddleware):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.max_retry_times = 5
        self.priority_adjust = 1

        project_settings = get_project_settings()
        self.request_proxy_url = project_settings['PROXY_API']
        self.proxy_ip = self.get_proxypool()
    def get_proxypool(self):
        return 'http://'+requests.get(self.request_proxy_url).text.strip()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        # request.meta["proxy"] = 'http://133.242.237.18:3128'
        request.meta["proxy"] = self.proxy_ip
        # return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        return response


    def process_exception(self, request, exception, spider):

        if '10061' in str(exception) or '10060' in str(exception) or '407' in str(exception) or isinstance(exception, TimeoutError):
            self.proxy_ip = self.get_proxypool()
            print(self.proxy_ip)
            request.meta['proxy'] = self.proxy_ip

        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class FailLogger(object):

  def __init__(self):
        project_settings = get_project_settings()
        self.mongo_uri = project_settings['MONGO_URI']
        self.mongo_db = project_settings['MONGO_DB']
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

  @classmethod
  def from_crawler(cls, crawler):
    ext = cls()
    crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
    return ext

  def spider_error(self, failure, response, spider):
    # print("Error on {0}, traceback: {1}".format(response.url, failure.getTraceback()))
    # RETRY_HTTP_CODES = [500, 502, 503, 504, 508, 400, 403, 404, 408, 520]
    if response.status != 404:
        self.col = self.db['spider_error']
        error_data = {"_id": response.url, "url": response.url, "status": response.status, "spider_name": spider.name,
                      "db": spider.collection, "table_name": spider.collection + '_error', "exception": str(failure.getTraceback())}
        try:
            self.col.insert_one(dict(error_data))
        except pymongo.errors.DuplicateKeyError as e:
            DropItem(f'{e.args[0]}')

    # with open("errlog.txt", "a") as f:
    #     f.write(spider.name + "\n")
    #     f.write(response.url + "\n")
    #     f.write(failure.getTraceback() + "\n")
    # return response



class GetFailedUrl(RetryMiddleware):

    def __init__(self, settings):
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def process_response(self, request, response, spider):

        # if response.status in self.retry_http_codes:
        #     # 将爬取失败的URL存下来，你也可以存到别的存储
        #     with open(str(spider.name) + ".txt", "a") as f:
        #         f.write(response.url + "\n")
        #     return response
        return response
    def process_exception(self, request, exception, spider):
        # 出现异常的处理
        # if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
        #     with open(str(spider.name) + ".txt", "a") as f:
        #         f.write(str(request) + "\n")
        return None


class PolicyCrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
