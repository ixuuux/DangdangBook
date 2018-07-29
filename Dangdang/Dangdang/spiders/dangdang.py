# -*- coding: utf-8 -*-
import json

import scrapy
from Dangdang.items import DangdangItem
from Dangdang import settings


class DangdangSpider(scrapy.Spider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    offset = 1
    url = "http://search.m.dangdang.com/search_ajax.php?keyword=python&act=get_product_flow_search&page={}"
    start_urls = [url.format(offset)]



    def parse(self, response):
        item = DangdangItem()
        products = json.loads(response.text)
        for product in products['products']:
            item['book_name'] = product.get('name')  # 书名
            item['author_name'] = product.get('authorname')  # 作者
            item['price'] = product.get('price')  # 现价
            item['original_price'] = product.get('original_price')  # 原价
            item['score'] = product.get('score')  # 评分
            item['stock'] = product.get('stock')  # 库存
            item['total_review_count'] = product.get('total_review_count')  # 评论数
            item['shop_id'] = product.get('shop_id')  # 店铺id
            item['shop_info'] = product.get('shop_info')  # 店铺名称
            item['publisher'] = product.get('publisher')  # 出版社
            item['publish_date'] = product.get('publish_date')  # 出版日期
            item['image_url'] = product.get('image_url')  # 图书封面
            item['product_url'] = product.get('product_url')  # 图书url
            yield item
            self.offset += 1
            if self.offset <= settings.MAX_PAGE:
                yield scrapy.Request(self.url.format(self.offset))
