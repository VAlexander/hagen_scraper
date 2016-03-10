# -*- coding: utf-8 -*-

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
