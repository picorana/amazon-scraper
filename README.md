# Amazon Scraper

Amazon-scraper is a command line application to collect reviews and questions/answerts from amazon products.

## Installation

## Usage

```bash
$ amazon-scraper B01MUSD2ST
```

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
