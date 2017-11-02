import unittest
import requests_mock
from amazon_scraper import AmazonScraper


class TestAmazon(unittest.TestCase):

	def setUp(self):

		args = {
		'asin':'a'
		}

		self.amazon_scraper = AmazonScraper(**args)

		#self.amazon_scraper.scrape()

	def test_a(self):
		assert (1+1)==2

	def test_parser(self):
		args = AmazonScraper.parse_args(['a'])
		assert args.asin