# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import pymongo
import pymongo.errors
import requests
from urllib.parse import urljoin
from twisted.internet.error import TimeoutError
from scrapy import signals, Request,FormRequest
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.spidermiddlewares.httperror import HttpError



class ScrapyCrawlerSpiderMiddleware():
    """
    爬虫中间件
    """
    def __init__(self):
        project_settings = get_project_settings()
        self.items_scraped = 0
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
        pass

    def spider_closed(self, spider):
        pass

    def item_scraped(self, item, spider):
        self.items_scraped += 1



class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
    随机UserAgent中间件
    """
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
    """
    代理IP中间件
    """
    def __init__(self):
        self.max_retry_times = 5
        self.priority_adjust = 1
        project_settings = get_project_settings()
        self.request_proxy_url = project_settings['PROXY_API']
        self.proxy_ip = self.get_proxypool()

    def get_proxypool(self):
        # 代理IP接口
        # 此处为开源项目proxy_pool的接口方式，可修改为购买的代理SDK接口逻辑
        # 项目地址：https://github.com/jhao104/proxy_pool
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
        # example: self.proxy_ip = 'http://133.242.237.18:3128'
        request.meta["proxy"] = self.proxy_ip

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        return response

    def process_exception(self, request, exception, spider):
        RETRY_HTTP_CODES = [10061,10060,407]
        if any([True if str(i) in RETRY_HTTP_CODES else False for i in str(exception)]) or isinstance(exception, TimeoutError):
            self.proxy_ip = self.get_proxypool()
            request.meta['proxy'] = self.proxy_ip
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class FailLogger(object):
    """
    错误警告中间件
    """
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

        # 将错误写入MongoDB
        if response.status != 404:
            self.col = self.db['spider_error']
            error_data = {"_id": response.url, "url": response.url, "status": response.status, "spider_name": spider.name,
                          "db": spider.collection, "table_name": spider.collection + '_error', "exception": str(failure.getTraceback())}
            try:
                self.col.insert_one(dict(error_data))
            except pymongo.errors.DuplicateKeyError as e:
                DropItem(f'{e.args[0]}')
        # 将错误写入文件
        # with open("error.log", "a") as f:
        #     f.write(spider.name + "\n")
        #     f.write(response.url + "\n")
        #     f.write(failure.getTraceback() + "\n")



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
    """
    下载中间件
    """
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
