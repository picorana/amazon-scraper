# Amazon Scraper

[![Documentation Status](https://readthedocs.org/projects/amazon-scraper/badge/?version=latest)](http://amazon-scraper.readthedocs.io/en/latest/?badge=master)
[![Build](https://travis-ci.org/picorana/amazon-scraper.svg?branch=master)](https://travis-ci.org/picorana/amazon-scraper.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/picorana/amazon-scraper/badge.svg?branch=master)](https://coveralls.io/github/picorana/amazon-scraper?branch=master)

Amazon-scraper is a command line application to collect reviews and questions/answers from amazon products.

Read the documentation here: [amazon-scraper on readthedocs](http://amazon-scraper.readthedocs.io/)

## Table of contents
* [Installation](#installation)
* [Usage](#usage)
* [Options](#options)
* [References](#references)

## Installation

### via pip

~ TODO

### cloning this repository

```bash
$ git clone https://github.com/picorana/amazon-scraper.git   
$ cd amazon-scraper
$ python setup.py install
```

## Usage

Run `amazon-scraper` via command line by running
```bash
$ amazon-scraper [asin]
```

`asin` is a unique identifier for a product on amazon. You can find it in the url:   
A query to `https://www.amazon.com/gp/product/B01H2E0J5M` would look like this:


```bash
$ amazon-scraper B01H2E0J5M
```

You can also insert multiple asins:

```bash
$ amazon-scraper B01H2E0J5M B01GYLZD8C B0736R3W1F
```

or load them from file:

```bash
$ amazon-scraper --file asins.txt
```

the file needs to have each asin on one line, like this:
```
B01H2E0J5M
B01GYLZD8C
B0736R3W1F
```
## Output

`amazon-scraper` downloads pages, reviews, questions and answers.   
It will save its output in folders:   

`pages` will contain the main pages of the product, useful for extracting more info about the product.   
You can disable this function by using the option `--save-pages`

`results` will contain the reviews, organized in json files.   
You can disable scraping the reviews by using the option `--no-reviews`

`questions` will contain the questions and answers, organized in json files.   
You can disable scraping the questions by using the option `--no-questions`


## Options

	positional arguments:
	  asin                  Amazon asin(s) to be scraped

	optional arguments:
	  -h, --help            show this help message and exit
	  --file FILE, -f FILE  Specify path to list of asins
	  --save-main-pages, -p
	                        Saves the main pages scraped
	  --verbose, -v         Logging verbosity level
	  --no-reviews          Do not scrape reviews
	  --no-questions        Do not scrape questions

## References
[instagram-scraper](https://github.com/rarcega/instagram-scraper) has been used as a reference for the structure of the program.   
[this blogpost](https://blog.hartleybrody.com/scrape-amazon/) has been very useful in understanding the issues of building a scraper.
