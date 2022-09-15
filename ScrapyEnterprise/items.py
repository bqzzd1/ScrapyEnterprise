# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import json
import scrapy


class Attachment(scrapy.Item):
    """附件"""

    fujian_title = scrapy.Field()
    fujian_link = scrapy.Field()


class PolicyItem(scrapy.Item):
    """政策数据"""

    id = scrapy.Field()
    detailUrl = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    plain_text = scrapy.Field()
    district = scrapy.Field()
    department = scrapy.Field()
    pub_department = scrapy.Field()
    posting_time = scrapy.Field()
    closing_time = scrapy.Field()
    address = scrapy.Field()
    policy_level = scrapy.Field()
    requirement = scrapy.Field()
    application_materials = scrapy.Field()
    support_amount = scrapy.Field()
    typeName = scrapy.Field()
    serverObject = scrapy.Field()
    tec_policy = scrapy.Field()
    fujian = scrapy.Field()
    images = scrapy.Field()
    extended_filed = scrapy.Field()

    def to_dict(self):
        data = dict(self)
        fujian = data.pop('fujian', None)
        data['fujian'] = []
        if isinstance(fujian, list):
            for f in fujian:
                if f:
                    data['fujian'].append(dict(f))
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)



