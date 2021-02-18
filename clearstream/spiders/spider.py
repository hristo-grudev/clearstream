import scrapy
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader
from ..items import ClearstreamItem
from itemloaders.processors import TakeFirst


class ClearstreamSpider(scrapy.Spider):
	name = 'clearstream'
	start_urls = ['https://www.clearstream.com/clearstream-en/search/1272944!search?state=H4sIAAAAAAAAADXMOwqFQAxG4a1c_noKbae9aG3hBgYnPkAnmkRUxL0rgt35mnMiBqNSeIJP6zi61zV_akNDpvDn5dAPphVJFTqCzzOHZSU54AEH7Xkr9nkQin9ORsm-g7I8_W5_kbTBdQO5n5bbdAAAAA&tf=1272428%3AHeadline']
	page = 0

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		self.page += 1
		next_page = f'https://www.clearstream.com/clearstream-en/search/1272944!search?state=H4sIAAAAAAAAADWNMQvCMBBG_4p8cwYbBOVWURw7uIlDaE4biIneXVEp_e9Kodt7y3sjYjA-Sn2AypCzm_1cF7uFjk1BIxq_9Ru_A11w4hBzKozr5NAn05alDXcGNWuH18DyBQEO2tf34fNMwnFfi3GxpatV_jzPVpG1w_QDwlW8PYoAAAA&sort=date+desc&hitsPerPage=10&pageNum={self.page}'

		if not post_links:
			raise CloseSpider('no more pages')

		yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		title = response.xpath('//div[@class="main-content"]/h1/text()').get()
		description = response.xpath('//div[@class="main-content"]//text()[normalize-space() and not(ancestor::h1 | ancestor::span[@class="timestamp"] | ancestor::table)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//span[@class="timestamp"]/text()').get()

		item = ItemLoader(item=ClearstreamItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
