import json
import re
import scrapy
from scrapy import FormRequest
from urllib.parse import urlencode

from scrapy.http import Request, HtmlResponse
from policy_crawler.items import PolicyItem,Attachment
from policy_crawler.spiders.utils import prepare_request, pq
from policy_crawler.spiders.utils import pq, prepare_request

from policy_crawler.spiders.utils import common_parse



DB_COLLECTION = 'policy_data'


class AnHuiSpider1(scrapy.Spider):
    name = 'anhui_zwfw1'
    website_name = '安徽政务服务平台'
    collection = DB_COLLECTION
    start_url='http://xc.ahzwfw.gov.cn/hqw-bsdt-web/policy/policyMatch/getMatchPage.do'
    zcwj_url='http://xc.ahzwfw.gov.cn/hqw-bsdt-web/policy/policyInfo/getRestPolicyInfoPage.do'
    cookies = {
          'JSESSIONID': '19F4FEE303534058F7DEF643FA1ED578',
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
         # 'Cookie': 'JSESSIONID=19F4FEE303534058F7DEF643FA1ED578',
        'Referer': 'http://xc.ahzwfw.gov.cn/hqw-bsdt-web/static/msjx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }

    item_List=[]

    def get_params(self,page):

        params = {
            'pageSize': '10',
            'pageNo': str(page),
            'total': '',
            'orgCode': '',
            'labelId': '',
            'areaCode': '',
            'state': '',
            'serviceName': '',
            'orderBy': '',
            'isMsjx': '1',
        }
        return params

    def start_requests(self):
        params = self.get_params(1)
        yield FormRequest(self.start_url,cookies=self.cookies,method='GET',formdata=params,
                              headers=self.headers,meta={'page': 1,}, dont_filter=True)

    def parse(self, response, **kwargs):
        page = response.meta['page'] + 1
        if response.json()['data']['records']:
            params = self.get_params(page)
            yield FormRequest(self.start_url, cookies=self.cookies, method='GET', formdata=params,
                              headers=self.headers, meta={'page': page,}, dont_filter=True)

        for i in response.json()['data']['records']:
            params = {'id': i['serviceId']}
            yield FormRequest(
                url='http://xc.ahzwfw.gov.cn/hqw-bsdt-web/policy/policyService/getPolicyService.do',
                method='GET',
                formdata=params,
                callback=self.parse_detail,
                meta={'url': 'http://xc.ahzwfw.gov.cn/hqw-bsdt-web/static/zcdx/detail?id='+i['serviceId'] },
                cb_kwargs={
                    'title':i['serviceName'],
                    'start_time': i['applyStartTime'],
                    'end_time': i['applyEndTime'],
                    'district':'安徽省-宣城市-'+i['areaName'],
                },
                dont_filter=True
            )

    def parse_detail(self,response, **kwargs):
        return PolicyItem({
            'detailUrl': response.meta['url'],
            'content': str(response.json()['data']),
            # 'plain_text': plain_text,
            'department': self.website_name,
            # 'fujian':fujian,
            # 'images': images,
            **kwargs
        })

    def close(self,spider, reason):

        print(self.item_List)
        print(len(self.item_List))



class AnHuiSpider2(scrapy.Spider):
    name = 'anhui_zwfw2'
    website_name = '安徽政务服务平台'
    collection = DB_COLLECTION
    start_url='http://xc.ahzwfw.gov.cn/hqw-bsdt-web/policy/policyInfo/getRestPolicyInfoPage.do'
    cookies = {
        'JSESSIONID': '19F4FEE303534058F7DEF643FA1ED578',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'JSESSIONID=19F4FEE303534058F7DEF643FA1ED578',
        'Referer': 'http://xc.ahzwfw.gov.cn/hqw-bsdt-web/static/zcwj',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }

    item_List=[]

    def get_params(self,page):

        params = {
            'pageSize': '10',
            'pageNo': str(page),
            'total': '',
            'orgCode': '',
            'publishArea': '',
            'labelId': '',
            'policyLevel': '',
            'state': '',
            'policyTitle': '',
        }
        return params

    def start_requests(self):
        params = self.get_params(1)
        yield FormRequest(self.start_url,cookies=self.cookies,method='GET',formdata=params,
                              headers=self.headers,meta={'page': 1,}, dont_filter=True)

    def parse(self, response, **kwargs):
        page = response.meta['page'] + 1
        if response.json()['data']['records']:
            params = self.get_params(page)
            yield FormRequest(self.start_url, cookies=self.cookies, method='GET', formdata=params,
                              headers=self.headers, meta={'page': page,}, dont_filter=True)

        for i in response.json()['data']['records']:
            fujian = [Attachment({
                'fujian_title': i['policyTitle'],
                'fujian_link': 'http://xc.ahzwfw.gov.cn/docview/view/url?url=xccnserver/'+i['policyFile']
            })]
            yield PolicyItem({
                'detailUrl': 'http://xc.ahzwfw.gov.cn/hqw-bsdt-web/static/zcwj/detail?id='+i['id'],
                'title': i['policyTitle'],
                'posting_time': i['publishTime'],
                'content':'',
                'district': '安徽省-宣城市',
                'department': i['policyOffice'],
                'fujian':fujian,
            })

    def close(self,spider, reason):

        print(self.item_List)
        print(len(self.item_List))

