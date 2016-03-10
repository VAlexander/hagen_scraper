# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy import signals, Request
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline

## CSV pipeline
class HagenPipeline(object):
	
	## Initialize unique key (UPC) and files
	def __init__(self):
		self.upcs_seen = set()
		self.files = {}
	
	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline
	
	## When spider opened, prepare csv exporter
	def spider_opened(self, spider):
		file = open('results.txt', 'w+b')
		self.files[spider] = file
		self.exporter = file
		#self.exporter.fields_to_export = ["title", "upc", "part_number", "msrp", "your_cost", "description", "breadcrumbs", "image_path"]
		#self.exporter.encoding = "utf-8"
		#self.exporter.start_exporting()
	
	## When spider closed, finish exporting and close the file
	def spider_closed(self, spider):
		self.exporter.close()
		file = self.files.pop(spider)
		file.close()

	## Processing each item
	def process_item(self, item, spider):
		if tuple(item.get('upc', '')) in self.upcs_seen:
			## Drop the item, it's duplicate
			raise DropItem("Duplicate item found: %s" % item)
		else:
			## Add its UPC to seen and export it to csv
			self.upcs_seen.add(item.get('upc'))
			
		try:
			item["msrp"] = item["msrp"].split("$")[-1].strip()
		except:
			pass
			
		try:
			item["your_cost"] = item["your_cost"].split("$")[-1].strip()
		except:
			pass
			
		try:
			if item["image_path"] != "No image":
				image_extension = item["image_path"].split(".")[-1]
				item["image_path"] = "img/%s.%s" % (item["upc"], image_extension)
		except:
			pass
		
		
		
		fields = (
			"title",
			"upc",
			"part_number",
			"msrp",
			"your_cost",
			"description",
			"breadcrumbs",
			"image_path"
			)
			
		for f in fields:
			try:
				if not item[f]:
					item[f] = ""
			except:
				item[f] = ""
				
		self.exporter.write("\"{0}\" \"{1}\" \"{2}\" \"{3}\" \"{4}\" \"{5}\" \"{6}\" \"{7}\"\n".format(item["title"],item["upc"],item["part_number"],item["msrp"],item["your_cost"],item["description"],item["breadcrumbs"],item["image_path"]))
		
		return item

## Image pipeline			
class HagenImagesPipeline(ImagesPipeline):
	## On recieving item yield its image_url field to new request
	def get_media_requests(self, item, info):
		if item['image_url']:
			yield Request(item['image_url'], meta={"upc":item["upc"]})

	def get_images(self, response, request, info):
		for key, image, buf, in super(HagenImagesPipeline, self).get_images(response, request, info):
			if "upc" in response.meta:
				extension = key.split(".")[-1].strip()
				key = "%s.%s" % (response.meta["upc"], extension)
			yield key, image, buf
			
	## When item is completed
	def item_completed(self, results, item, info):
		## Get the first path (may be more, but for this site only 1 image is presented)
		image_path = [x['path'] for ok, x in results if ok]
		if len(image_path) > 0:
			image_path = image_path[0]
		## If got no image
		if not image_path:
			## Print "no image" in the image_path field
			item['image_path'] = "No image"
		## Otherwise
		else:
			## Set item's image path
			item['image_path'] = image_path
		## And return the item
		return item