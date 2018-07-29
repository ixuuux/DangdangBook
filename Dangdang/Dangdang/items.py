# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangItem(scrapy.Item):
    book_name = scrapy.Field()
    author_name = scrapy.Field()
    price = scrapy.Field()
    original_price = scrapy.Field()
    score = scrapy.Field()
    stock = scrapy.Field()
    total_review_count = scrapy.Field()
    shop_id = scrapy.Field()
    shop_info = scrapy.Field()
    publisher = scrapy.Field()
    publish_date = scrapy.Field()
    image_url = scrapy.Field()
    product_url = scrapy.Field()

