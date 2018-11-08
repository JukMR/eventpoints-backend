import scrapy
import textwrap
from scrapy.spiders import CrawlSpider
from eventscraper.items import Event


class MeetupSpider(CrawlSpider):
    name = 'meetup'
    allowed_domains = ['meetup.com']
    start_urls = ['https://www.meetup.com/find/events/tech/']

    def parse(self, response):
        tech_meetups = response.xpath('//div[@class="chunk"]')
        for tech_meetup in tech_meetups:
            event = Event()
            event['source'] = {}
            event['source']['event_url'] = response.request.url
            event['source']['name'] = 'Meetup'
            event['source']['logo'] = 'https://secure.meetupstatic.com/s/img/5455565085016210254/logo/svg/logo--script.svg'
            event['source']['url'] = 'https://www.meetup.com'

            event['title'] = tech_meetup.xpath('a/span/text()').extract_first()
            event['group'] = tech_meetup.xpath('div/a/span/text()').extract_first()

            details_url = tech_meetup.xpath('a/@href').extract_first()

            yield scrapy.Request(details_url, callback=self.parse_details, meta={'event': event})

    @staticmethod
    def parse_details(response):
        event = response.meta['event']

        details = response.xpath('//div[contains(@class, "event-description")]/p').extract_first()
        event['host'] = response.xpath('//div[contains(@class, "event-info-hosts-text")]/a/span/span/span/text()').extract_first()
        event['short_details'] = textwrap.shorten(details, width=50, placeholder="...")
        event['details'] = details

        event['price'] = {}
        event['price']['is_free'] = True

        event['date'] = {}
        event['date']['datetime'] = response.xpath('//time/@datetime').extract_first()

        location = response.xpath('//address/p/text()').extract()
        event['location'] = {}
        event['location']['name'] = location[0]
        event['location']['address'] = location[1]
        event['location']['lat'] = '40.392303'
        event['location']['lng'] = '-3.697430'

        yield event
