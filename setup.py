import sys
from setuptools import setup, find_packages

setup(
	name='amazon-scraper',
	version='0.0.1',
	description='amazon-scraper is a command line application written in Python '
				'it downloads reviews and questions/answers from amazon products',
	url='',
	download_url='',
	author='picorana',
	author_email='',
	license='Public domain',
	packages=find_packages(),
	install_requires=[],
	entry_points={
		'console_scripts': ['amazon-scraper=amazon_scraper.app:main']
	},
	zip_safe=False,
	keywords=['amazon', 'scraper', 'reviews', 'questions', 'downloads', 'products']
)
