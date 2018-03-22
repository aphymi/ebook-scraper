#!/usr/bin/python3

import sys
import time

from lxml import html
from lxml.etree import strip_tags
import requests

from scraper import Scraper


class APGtE_Scraper(Scraper):
	author = "erraticerrata"
	subtitle = "Do Wrong Right"
	
	def get_toc(self):
		toc = html.fromstring(requests.get("https://practicalguidetoevil.wordpress.com/table-of-contents/").content)
		content = toc.xpath("//div[@class=\"entry-content\"]")[0]
		children = content.getchildren()
		
		num_books = 0
		# Count the number of currently-out books.
		# In APGtE's toc's element tree, every second child is a book heading.
		while children[num_books*2].tag == "h2" and children[num_books*2].text.startswith("Book"):
			num_books += 1
		
		self.books = []
		for i in range(num_books):
			book = {"name": children[i * 2].text, "chapters": []}
			# For some reason, book 1 uses roman numerals, unlike the others. Just change it.
			if book["name"] == "Book I":
				book["name"] = "Book 1"
			
			book["title"] = "A Practical Guide to Evil - " + book["name"]
			book["subtitle"] = self.subtitle
			book["file"] = "apgte_" + book["name"].replace(" ", "_").lower() + ".epub"
			
			book_children = children[i * 2 + 1].getchildren()
			# For some reason, book 2's chapter list has an extra two layers of tags.
			if book["name"] == "Book 2":
				book_children = book_children[0].getchildren()[0].getchildren()
			
			chaps = [chap.getchildren()[0] for chap in book_children]
			
			for chap in chaps:
				book["chapters"].append({"name": chap.text, "link": chap.get("href")})
			
			self.books.append(book)
	
	@staticmethod
	def get_chapter_data(chapter):
		# Be nice. Don't spam the server.
		time.sleep(1)
		r = requests.get(chapter["link"])
		if r.status_code != 200:
			print("Error! Non-200 status code: " + str(r.status_code))
			raise Exception
		
		page = html.fromstring(r.content)
		chapter["date"] = page.xpath("//time[contains(@class, 'entry-date')]")[0].text
		
		chapter["content"] = page.xpath("//div[@class='entry-content']")[0]
		# Remove ads and social media buttons from the tree.
		chapter["content"].remove(chapter["content"].getchildren()[-2])
		chapter["content"].remove(chapter["content"].getchildren()[-1])
		
		# Strip out any links, just in case.
		strip_tags(chapter["content"], "a")


if __name__ == "__main__":
	APGtE_Scraper().scrape(*sys.argv[1:])
