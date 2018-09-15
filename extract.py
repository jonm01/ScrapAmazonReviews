#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
#https://www.amazon.com/product-reviews/B06Y14T5YW/?pageNumber=2
#Add some recent user agent to prevent amazon from blocking the request
#Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
#This script has only been tested with Amazon.com

from lxml import html
import json
import requests
import json,re
import math
from dateutil import parser as dateparser
from time import sleep
def productInfo(asin):
	amazon_url  = 'http://www.amazon.com/dp/product-reviews/'+asin

	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(amazon_url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	XPATH_PRODUCT_NAME = '//h1//a[@data-hook="product-link"]//text()'
	XPATH_PRODUCT_PRICE  = '//span[@class="a-color-price arp-price"]/text()'
	XPATH_TOTAL_REVIEWS= '//span[@data-hook="total-review-count"]/text()'

	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	product_price = ''.join(raw_product_price).replace(',','')

	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).strip()
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)

	count1 = parser.xpath(XPATH_TOTAL_REVIEWS)
	count=''.join(count1).replace(',','')
	p= math.ceil(int(count)/10)

	reviews_list = []
	ratings_dict = {}

	#grabing the rating  section in product page
	for ratings in total_ratings:
		extracted_rating = ratings.xpath('./td//a//text()')
		if extracted_rating:
			rating_key = extracted_rating[0]
			raw_raing_value = extracted_rating[1]
			rating_value = raw_raing_value
			if rating_key:
				ratings_dict.update({rating_key:rating_value})


	for x in range(p):
		reviews_list=reviews_list+ParseReviews(asin,x+1)


	data = {
				'name':product_name,
				'url':amazon_url,
				'price':product_price,
				'count':count,
				'ratings':ratings_dict,
				'reviews':reviews_list
			}
	return data

def ParseReviews(asin,page):
	amazon_url  = 'http://www.amazon.com/dp/product-reviews/'+asin+'/?pageNumber='+str(page)

	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(amazon_url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
	XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
	reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

	if not reviews:
		reviews = parser.xpath(XPATH_REVIEW_SECTION_2)

	ratings_dict = {}
	reviews_list1 = []

	if not reviews:
		raise ValueError('unable to find reviews in page')
	#Parsing individual reviews
	for review in reviews:
		XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
		XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
		XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
		XPATH_REVIEW_TEXT_1 = './/span[@data-hook="review-body"]//text()'
		XPATH_AUTHOR  = './/a[@data-hook="review-author"]//text()'

		raw_review_author = review.xpath(XPATH_AUTHOR)
		raw_review_rating = review.xpath(XPATH_RATING)
		raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
		raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
		raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)

		#cleaning data
		author = ' '.join(' '.join(raw_review_author).split())
		review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
		review_header = ' '.join(' '.join(raw_review_header).split())

		try:
			review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
		except:
			review_posted_date = None
		review_text = ' '.join(' '.join(raw_review_text1).split())

		review_dict = {
							'review_text':review_text,
							'review_posted_date':review_posted_date,
							'review_header':review_header,
							'review_rating':review_rating,
							'review_author':author

						}
		reviews_list1.append(review_dict)
	return reviews_list1


def ReadAsin():
	#Add your own ASINs here
	AsinList = ['B07BBRCH91',]
	extracted_data = []
	for asin in AsinList:
		print("Downloading and processing page http://www.amazon.com/dp/"+asin)
		extracted_data.append(productInfo(asin))
		sleep(5)
	f = open('data.json','w')
	json.dump(extracted_data,f,indent=4)

if __name__ == '__main__':
	ReadAsin()
