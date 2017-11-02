import unittest
import httpretty
import requests
from amazon_scraper import AmazonScraper
from amazon_scraper.constants import *


class TestAmazon(unittest.TestCase):

	def setUp(self):

		args = {
		'asin':'a'
		}

		self.amazon_scraper = AmazonScraper(**args)

		#self.amazon_scraper.scrape()

	def test_single_asin(self):
		args = AmazonScraper.parse_args(['a'])
		assert args.asin

	def test_asin_file(self):
		with self.assertRaises(ValueError):
			AmazonScraper.parse_args(['a', '--file', 'b'])

	def test_no_asins(self):
		with self.assertRaises(ValueError):
			AmazonScraper.parse_args([])

	"""
	@httpretty.activate
	def test_retrieve_page(self):
		with self.assertRaises(RuntimeError):
			httpretty.register_uri(httpretty.GET, base_product_page_url + 'a', body="", status=404)
			self.amazon_scraper.proxies = ['1.2.3.4', '1.2.3.5']
			self.amazon_scraper.retrieve_page('a')
	

	@httpretty.activate
	def test_no_reviews_no_questions(self):
		args = AmazonScraper.parse_args(['a', '--no-reviews', '--no-questions'])
		self.amazon_scraper.no_reviews = True
		self.amazon_scraper.no_reviews = True
		httpretty.register_uri(httpretty.GET, base_product_page_url + 'a', body="")
		self.amazon_scraper.scrape()
	"""


	@httpretty.activate
	def test_get_proxies(self):
		httpretty.register_uri(httpretty.GET, 'https://free-proxy-list.net/anonymous-proxy.html', body="", status=404)
		httpretty.register_uri(httpretty.GET, 'https://www.us-proxy.org/', body="", status=404)
		httpretty.register_uri(httpretty.GET, 'https://www.sslproxies.org/', body="", status=404)
		httpretty.register_uri(httpretty.GET, 'https://www.socks-proxy.net/', body="", status=404)

		with self.assertRaises(requests.ConnectionError):
			self.amazon_scraper.get_proxies()


	def test_parse_asins_from_file(self):
		res = AmazonScraper.parse_asins_from_file('amazon_scraper/tests/fixtures/test_parse_asins_from_file.txt')
		assert res == ['aaa', 'bbb']

	@ httpretty.activate
	def test_httpretty(self):
		httpretty.register_uri(httpretty.GET, "http://yipit.com/", body="Find the best daily deals")
		