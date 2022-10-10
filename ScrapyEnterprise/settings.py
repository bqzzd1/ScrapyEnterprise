# Scrapy settings for ScrapyEnterprise project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from pathlib import Path
from dotenv import dotenv_values

ENV = dotenv_values(Path(os.getcwd(), '.env'))
LOG_LEVEL = ENV.get('LOG_LEVEL', 'INFO')


BOT_NAME = 'ScrapyEnterprise'
SPIDER_MODULES = ['ScrapyEnterprise.spiders']
NEWSPIDER_MODULE = 'ScrapyEnterprise.spiders'
COMMANDS_MODULE = 'ScrapyEnterprise.commands'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ScrapyEnterprise (+http://www.yourdomain.com)'

# 是否遵循robot协议
ROBOTSTXT_OBEY = False
# 重定向禁止
# REDIRECT_ENABLED = False

RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-Hans',
    'DNT': '1'
}



# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'ScrapyEnterprise.middlewares.ScrapyCrawlerSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 代理IP中间件
    # 'ScrapyEnterprise.middlewares.ProxyDownloaderMiddleware': 10,
    # 随机UserAgent中间件
    'ScrapyEnterprise.middlewares.RotateUserAgentMiddleware': 200,
    # 邮件警告中间件
    # 'ScrapyEnterprise.middlewares.GetFailedUrl': 600,
    # 请求重试中间件
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}



# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    # 错误警告中间件
    'ScrapyEnterprise.middlewares.FailLogger': 599,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'ScrapyEnterprise.pipelines.ProcessPipeline': 50,
   'ScrapyEnterprise.pipelines.PersistPipeline': 100,
    # scrapy-redis
    # 'crawlab.CrawlabPipeline': 300,
    # 'scrapy_redis.pipeline.RedisPipeline':150,
}

# 项目管道最大并发数
CONCURRENT_ITEMS=100
# scrapy下载器最大并发数
CONCURRENT_REQUESTS=500
# 如果遇到阻塞IO不足的问题，请增加此值
REACTOR_THREADPOOL_MAXSIZE = 50


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
DOWNLOAD_DELAY = 0 #限速
RANDOMIZE_DOWNLOAD_DELAY=True #*0.5-1.5随机值
DOWNLOAD_TIMEOUT = 10
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5.0
AUTOTHROTTLE_MAX_DELAY = 60.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = LOG_LEVEL == 'DEBUG'


# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# scrapy_redis
# https://scrapy-redis.readthedocs.io/en/v0.6.x/readme.html
# REDIS_URL = ENV['REDIS_URL']
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
# SCHEDULER_DEBUG = LOG_LEVEL == 'DEBUG'
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# DUPEFILTER_DEBUG = LOG_LEVEL == 'DEBUG'
# STATS_CLASS = 'scrapy_redis.stats.RedisStatsCollector'
# SCHEDULER_PERSIST = True # 是否在关闭时候保留原来的调度器和去重记录，True=保留，False=清空
# SCHEDULER_FLUSH_ON_START = False  # 是否在开始之前清空 调度器和去重记录，True=清空，False=不清空

# OTHER SETTINGS
# PROC_API = ENV['PROC_API']
# FILT_API = ENV['FILT_API']
# APP_API = ENV['APP_API']
# APP_TOKEN = ENV['APP_TOKEN']
MONGO_URI = ENV['MONGO_URI']
MONGO_DB = ENV['MONGO_DB']
# AMQP_URL = ENV['AMQP_URL']
# AMQP_QUEUE = ENV['AMQP_QUEUE']
CRAWL_PAGE = int(ENV['CRAWL_PAGE'])  # -1: 爬所有页
# PROXY_API = ENV['PROXY_API']

