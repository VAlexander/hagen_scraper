# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HagenItem(scrapy.Item):
	title = scrapy.Field()
	upc = scrapy.Field()
	part_number = scrapy.Field()
	msrp = scrapy.Field()
	your_cost = scrapy.Field()
	description = scrapy.Field()
	breadcrumbs = scrapy.Field()
	image_url = scrapy.Field()
	image_path = scrapy.Field()
