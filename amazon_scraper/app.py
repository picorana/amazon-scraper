# TODO:
# * import list of asins from file
# * ability to change proxy sources
# * manage ssl errors!! 
# * manage timeouts
# * and manage wait time
# * manage quiet
# * manage destination
# * manage ignore_dups

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint
from math import *
import requests
import random
import logging
import argparse
import threading, Queue
import time
import json
import re
import os, sys 

from constants import *

class AmazonScraper(object):
	"""Hello, this is AmazonScraper!"""

	def __init__(self, **kwargs):

		default_attr = dict(
			asin = [],
			verbose=False,
			quiet=False,
			ignore_dups=False,
			no_reviews = False,
			no_questions = False,
			destination='./',
			save_pages=True
			)

		allowed_attr = list(default_attr.keys())
		default_attr.update(kwargs)

		for key in default_attr:
			if key in allowed_attr: self.__dict__[key] = kwargs.get(key)

		self.logger = AmazonScraper.get_logger(level=logging.DEBUG, verbose=default_attr.get('verbose'))

		# initialize a user agent generator
		self.ua = UserAgent()
		self.wait_time = 0.2


	def scrape(self):
		"""Manages the whole scraping process"""

		for asin in self.asin: 

			self.logger.info("Examining product " + asin)

			# collect a list of proxies
			# this is updated for each product,
			# I think it would be better to update it each time
			# too many proxies get banned by amazon
			self.proxies = self.get_proxies()

			# collect the reviews url and the total amount
			# of pages to be scraped
			main_reviews_url, review_pages_number = self.retrieve_page(asin)

			if not self.no_reviews:
				# scrape the reviews
				reviews, failed_urls = self.retrieve_reviews(main_reviews_url, review_pages_number)
				reviews_list = list(reviews.queue)
				failed_urls_list = list(failed_urls.queue)

				# log the number of results found
				self.logger.info("found " + str(len(reviews_list)) + " reviews for product " + asin)
				self.logger.info("failed " + str(len(failed_urls_list)) + " requests for product " + asin)

				# save the results to file
				if not os.path.exists('./reviews'): os.makedirs('./reviews')
				results_file = open("./reviews/" + asin + ".json", 'w+')
				for i in reviews_list: 
					json.dump(i, results_file)
					results_file.write('\n')

			# switch this if true with param about 
			if not self.no_questions:
			 	questions, fails = self.retrieve_questions(asin)

			 	questions_list = list(questions.queue)
			 	fails_questions_list = list(fails.queue)

			 	self.logger.info("found " + str(len(questions_list)) + " questions for product " + asin)
			 	self.logger.info("failed " + str(len(fails_questions_list)) + " urls for product " + asin)

			 	# save questions to file
				if not os.path.exists('./questions'): os.makedirs('./questions')
				questions_file = open("./questions/" + asin + ".json", 'w+')
				for i in questions_list: 
					json.dump(i, questions_file)
					questions_file.write('\n')			 	


	def retrieve_questions(self, asin):
		"""Scrapes the questions pages and returns a list
			of dicts containing questions and respecitive answers"""

		threads = []
		results = Queue.Queue()
		fails = Queue.Queue()

		for page_num in range(1, 100):
			t = threading.Thread(
				target=self.scrape_page_questions,
				args=(asin, page_num, fails, results)
				)
			t.start()
			threads.append(t)

		for thread in threads:
			thread.join()

		return results, fails


	def scrape_page_questions(self, asin, page_num, fails, results):
		"""threads to request and scrape a single questions page"""
		
		url = base_questions_url + asin + '/' + str(page_num)

		attempt = 0

		while attempt < 10 :
			try:
				res = requests.get(url,
					timeout = 20, 
					proxies = { 'http' : random.sample( self.proxies, 1 )},
					headers = { 'User-Agent' : self.ua.random}
					)

				if res.status_code != 200:
					raise RuntimeError("Server not responding: status code " + str(res.status_code) + " for url " + url)
				elif BeautifulSoup(res.content, 'html.parser').title.text == "Robot Check":
					raise RuntimeError("Robot Check not passed for url " + url)
				else:
					soup = BeautifulSoup(res.content, 'html.parser')
					question_boxes = soup.find_all("div", {"class":"a-fixed-left-grid-col a-col-right"})

					for j, box in enumerate(question_boxes):
						q_a_dict = {}

						if j==0: continue
						for k, question in enumerate(box.find_all("div", {"class":"a-fixed-left-grid-col a-col-right"})):
							if k==0:
								q_a_dict['question'] = question.a.text.strip()
						for k, answer in enumerate(box.find_all("div", {"class":"a-fixed-left-grid-col a-col-right"})):
							if k!=0: 
								ranswer = ""
								if answer.find("span", {"class":"askLongText"}):
									ranswer = answer.find("span", {"class":"askLongText"}).text
									ranswer = ranswer.strip()[:-8]
								else: 
									ranswer = answer.span.text
								q_a_dict['answer'] = ranswer.strip()
						if 'answer' in q_a_dict and 'question' in q_a_dict: 
							results.put(q_a_dict)

					return

			except requests.exceptions.Timeout:
				self.logger.debug("Connection timed out for url " + url)
			except requests.exceptions.RequestException as err:
				self.logger.debug(err)
			except RuntimeError as err:
				self.logger.debug(err)
			except KeyboardInterrupt:
				self.logger.warning('Keyboard interrupt received')
				sys.exit()
			attempt += 1

		self.logger.debug("failed url " + url + " after several attempts")
		fails.put(url)


	def retrieve_reviews(self, main_reviews_url, review_pages_number):
		"""Collects the review given the url of the reviews page"""
		
		results = Queue.Queue()
		fails = Queue.Queue()
		threads = []		

		# craft the single review page url
		url_parts = (base_amazon_url + main_reviews_url[1:]).strip().split("/")

		params = url_parts[-1].split('&')

		for page_num in range(1, review_pages_number):

			chosen_params = ['ref=cm_cr_dp_d_show_all_btm_'+str(page_num)+'?ie=UTF8', 'pageNumber='+str(page_num)]

			final_url = "https:/"

			for i, item in enumerate(url_parts):
				if i < (len(url_parts)-1) and i>0: final_url += item + '/'

			for param in chosen_params:
				final_url += param + '&'

			final_url = final_url[:-1]
			
			t = threading.Thread(
				target=self.scrape_page_reviews, 
				args=(final_url, fails, results)
				)

			t.start()
			threads.append(t)

		for thread in threads:
			thread.join()

		return results, fails


	def scrape_page_reviews(self, url, fails, results):
		"""threads to request and scrape a single review page"""
		
		attempt = 0

		while attempt < 10 :
			try:
				res = requests.get(url,
					timeout = 20, 
					proxies = { 'http' : random.sample( self.proxies, 1 )},
					headers = { 'User-Agent' : self.ua.random}
					)

				if res.status_code != 200:
					raise RuntimeError("Server not responding: status code " + str(res.status_code) + " for url " + url)
				elif BeautifulSoup(res.content, 'html.parser').title.text == "Robot Check":
					raise RuntimeError("Robot Check not passed for url " + url)
				else:
					soup = BeautifulSoup(res.content, 'html.parser')
					review_boxes = soup.find_all("div", {"class":"review"})

					for box in review_boxes:
						review = {}
						review['title'] = box.find("a", {"class":"review-title"}).text
						review['text'] = box.find("span", {"class":"review-text"}).text
						review['date'] = box.find("span", {"class":"review-date"}).text
						review['rating'] = box.find("i", {"class":"review-rating"}).span.text
						review['author'] = box.find("a", {"class":"author"}).text
						review['author_id'] = box.find("a", {"class":"author"}).get('href').split('/')[4]
						results.put(review)

					self.logger.info("finished scraping " + url)
					return

			except requests.exceptions.Timeout:
				self.logger.debug("Connection timed out for url " + url)
			except requests.exceptions.RequestException as err:
				self.logger.debug(err)
			except RuntimeError as err:
				self.logger.debug(err)
			except KeyboardInterrupt:
				self.logger.warning('Keyboard interrupt received')
				sys.exit()
			attempt += 1

		self.logger.debug("failed url " + url + " after several attempts")
		fails.put(url)


	def retrieve_page(self, asin):
		"""Requests the main product page, saves it, and returns an url for the reviews"""

		attempt = 0

		while attempt < 10: 

			# craft a request
			res = requests.get(base_product_page_url + asin, 
				proxies = { 'http' : random.sample( self.proxies, 1 )},
				headers = { 'User-Agent' : self.ua.random}
				)

			# if the asin does not exist, exit.
			if res.status_code == 404:
				self.logger.error("Asin " + asin + " does not exist")
				raise RuntimeError("Asin " + asin + " does not exist")
			# if the connection fails, try again
			elif res.status_code != 200:
				self.logger.error("Connection error on asin " + asin)
			# if everything goes well, scrape
			else:
				soup = BeautifulSoup(res.content, 'html.parser')

				# eventually amazon discovers us. 
				# in this case, try again with another proxy
				if soup.title.text == "Robot Check":
					self.logger.warning("Robot Check received")
				else:

					# save the page if the user specified to
					if self.save_pages:
						if not os.path.exists('./pages'):
							os.makedirs('./pages')
						page_file = open("./pages/" + asin + '.html', 'w+')
						page_file.write(res.content)
					
					reviews_url = soup.find(
						"div", { "id" : "reviews-medley-footer" }
						).find(
						"a", { "class" : "a-link-emphasis" }
						).get("href")

					if soup.find("div", {"id":"reviews-medley-footer"}) != None:
						review_pages_number = int(ceil(float(soup.find("div", {"id":"reviews-medley-footer"}).a.text
							.split("See all ")[1]
							.split(" customer")[0])/10))
					else: review_pages_number = 0

					return reviews_url, review_pages_number

		raise RuntimeError("Fetching product " + asin + " failed after several attempts.")


	def get_proxies(self):
		"""Retrieves a list of proxies"""

		proxies = set()

		# eventually put this somewhere else
		proxy_sources = [
			'https://free-proxy-list.net/anonymous-proxy.html', 
			'https://www.us-proxy.org/', 
            'https://www.sslproxies.org/', 
            'https://www.socks-proxy.net/'
		]

		# count times this is executed. stop at 10 attempts.
		attempt = 0
		while not len(proxies) > 0:
			for source in proxy_sources:
				res = requests.get(source, headers={
					'User-Agent':self.ua.random
					})

				if res.status_code != 200:
					self.logger.error("connection error " + str(res.status_code) \
						+ " source " + source)
				else:
					soup = BeautifulSoup(res.content, 'html.parser')
					tab = soup.find("table", {"id":"proxylisttable"})
					for cell in tab.find_all('td'):
						if cell.string != None and re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', cell.string) != None: 
							proxies.add(cell.string)
			
			self.logger.info("found " + str(len(proxies)) + " proxies")

			if not len(proxies) > 0:
				attempt += 1
				if attempt >= 10:
					raise ConnectionError("Failed to \
						retrieve any proxy after several \
						attempts, check your connection status")
				time.sleep(0.5)
			else:
				break

		return proxies


	@staticmethod
	def get_logger(level=logging.DEBUG, verbose=False):
		"""Returns a logger"""

		logger = logging.getLogger(__name__)

		fh = logging.FileHandler('scrape.log', 'wa')
		fh.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
		fh.setLevel(level)
		logger.addHandler(fh)

		sh = logging.StreamHandler(sys.stdout)
		sh.setFormatter( logging.Formatter('%(levelname)s: %(message)s') )
		if verbose:
			sh.setLevel(logging.DEBUG)
		else:
			sh.setLevel(logging.ERROR)
		logger.addHandler(sh)

		logger.setLevel(level)

		return logger

	@staticmethod
	def parse_asins_from_file(path):
		"""Reads a list of asins from a file"""
		
		asins = []

		try:
			file_to_read = open(path, 'r')
			for line in file_to_read:
				asins.append(line.strip())
		except IOError as err:
			raise ValueError("File not found " + err)

		return asins

	

def main():

	parser = argparse.ArgumentParser(
		description = "amazon-scraper downloads questions and reviews from amazon products",
		formatter_class = argparse.RawDescriptionHelpFormatter,
		fromfile_prefix_chars='@'
		)

	parser.add_argument('asin', help='Amazon asin(s) to be scraped', nargs='*')
	parser.add_argument('--file', '-f', help='Specify path to list of asins')
	parser.add_argument('--save-pages', '-p', action='store_true', default=True, help='Saves the main pages scraped')
	parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Logging verbosity level')
	parser.add_argument('--no-reviews', action='store_true', default=False, help='Do not scrape reviews')
	parser.add_argument('--no-questions', action='store_true', default=False, help='Do not scrape questions')
	parser.add_argument('--destination', '-d', default='./', help="Set a destination folder")
	parser.add_argument('--ignore-dups', action='store_true', help="Do not consider previous operations")
	parser.add_argument('--quiet', '-q', default=False, action='store_true', help='Be quiet while scraping')

	args = parser.parse_args()
	
	if not args.asin and args.file is None:
		parser.print_help()
		raise ValueError('Please provide asin or filename.')
	elif args.asin and args.file:
		parser.print_help()
		raise ValueError('Please provide only one of the following: asin(s) or filename')
	
	if args.file:
		args.asin = AmazonScraper.parse_asins_from_file(args.file)

	scraper = AmazonScraper(**vars(args))

	scraper.scrape() 


if __name__ == '__main__':
	main()