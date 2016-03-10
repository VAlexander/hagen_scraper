# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from hagen.items import HagenItem

try:
    import login_info
except ImportError:
    raise ImportError("You don't have login and password specified. \
	Create file 'login_info.py' with strings 'hagen_username' and 'hagen_password' \
	in spiders folder.")

class MainSpider(scrapy.Spider):
	name = "main"
	allowed_domains = ["hagendirect.com", "ecsrv.com"]
	start_urls = (
		'https://www.ecsrv.com/PrivateClientLogin.aspx?No=hagenusa',
	)
	
	hagen_username = login_info.hagen_username
	hagen_password = login_info.hagen_password
	
	categories_xpath = "//ul[@class='navigation']/li[4]/*//a"
	products_xpath = "//div[@class='prod_name']/a"
	next_page_xpath = "//a[contains(text(),'Next')]/@href"
	
	product_paths = {"title": "//div[@class='product_name'][1]/b/text()",
	"part_number": "//div[@class='product_name'][2]/text()",
	"upc": "//div[@class='product_name'][3]/text()",
	"msrp": "//div[@class='product_cost_msrp']/text()",
	"your_cost": ["//div[@class='product_new_cost']/text()", "//div[@class='product_cost']/text()"],
	"description": "//div[@id='tabs_ItemTabContent1']/text()",
	"breadcrumbs": "string(//div[@class='CategoryPath'])",
	"image_url": "//a[@class='ItemGalleryHiResImageLink']/@href"}
	
	session_code_xpath = "//input[@name='SessionCode']/@value"
	
	def parse(self, response):
		form_data = {}
		
		form_data["ClientID"] = self.hagen_username
		form_data["Password"] = self.hagen_password
		form_data["SessionCode"] = response.xpath(self.session_code_xpath).extract()[0]
		form_data["No"] = "hagenusa"
		form_data["Login"] = "LOGIN / CONNECTEZ-VOUS"
		
		return FormRequest.from_response(response, formdata=form_data,callback=self.after_login)
		
	def after_login(self, response):
		for category in response.xpath(self.categories_xpath):
			category_url = category.xpath("./@href").extract()[0]
			yield scrapy.Request(category_url, callback=self.parse_product_page)
			
	def parse_product_page(self, response):
		for product in response.xpath(self.products_xpath):
			product_url = product.xpath("./@href").extract()[0]
			yield scrapy.Request(product_url, callback=self.parse_product)
		if response.xpath(self.next_page_xpath):
			next_page_url = "http://www.hagendirect.com" + response.xpath(self.next_page_xpath).extract()[0]
			yield scrapy.Request(next_page_url, callback=self.parse_product_page)
	
	def parse_product(self, response):
		i = HagenItem()
		for field, xpath in self.product_paths.iteritems():
			if not isinstance(xpath, list):
				if response.xpath(xpath):
					i[field] = response.xpath(xpath).extract()[0].strip()
			else:
				for x in xpath:
					if response.xpath(x):
						i[field] = response.xpath(x).extract()[0].strip()
						break
		return i
				