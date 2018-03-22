from lxml.etree import tostring

from ebook import EPub, s_words


class Scraper:
	def __init__(self):
		# Instance variables that PyCharm will complain about if I don't define them here.
		self.title = ""
		self.author = ""
		self.books = []
	
	def scrape(self, *particular_books):
		self.get_toc()
		
		if particular_books:
			for book in particular_books:
				self.assemble_book(self.books[int(book) - 1])
		else:
			for book in self.books:
				self.assemble_book(book)
	
	def assemble_book(self, book):
		print("Beginning assembly of book: " + book["name"])
		book_words = 0
		ebook = EPub(book["title"], self.author)
		
		for chap in book["chapters"]:
			self.get_chapter_data(chap)
			
			# Count words by removing all tags, splitting text along whitespace, and counting the number of elements.
			chap["words"] = len(chap["content"].text_content().split())
			book_words += chap["words"]
			
			# Make the chapter header.
			title = chap["content"].makeelement("h2")
			title.text = chap["name"]
			# Subheader.
			sub = chap["content"].makeelement("h3")
			sub.text = "Published on {} | {}k words".format(chap["date"], s_words(chap["words"]))
			
			# Add in the header and subheader.
			chap["content"].insert(0, title)
			chap["content"].insert(1, sub)
			
			# Wrap the content in some html to make the ebook slightly more standards-compliant.
			html_tag = chap["content"].makeelement("html")
			html_tag.set("xmlns", "http://www.w3.org/1999/xhtml")
			head_tag = chap["content"].makeelement("head")
			body_tag = chap["content"].makeelement("body")
			html_tag.insert(0, head_tag)
			html_tag.insert(1, body_tag)
			body_tag.insert(0, chap["content"])
			
			ebook.add_chapter(chap["name"], tostring(html_tag, encoding="unicode"))
			# Minimise memory use by deleting the content now that it's saved elsewhere.
			del chap["content"]
			
			print("Finished assembling chapter: {} ({}k words)".format(chap["name"], s_words(chap["words"])))
		
		ebook.set_cover(book["title"], book["subtitle"], "by {} | {}k words".format(self.author, s_words(book_words)))
		ebook.output_file(book["file"])
		print("Finished assembling book: {} ({}k words)".format(book["file"], s_words(book_words)))
	
	def get_toc(self):
		"""
		Get an iterable of dicts (books) containing iterables of dicts (chapters).
		
		Each book dict must contain at least the following keys:
		
		name ------ individual name of the book, separate from any series.
		title ----- the title of the book, including mention of the series, if any.
		file ------ the name the book's epub file should have.
		chapters -- an iterable of dicts which must each contain any information needed to get the content and metadata
						of a single chapter.
						
		They may also contain a "subtitle" key, with the subtitle of the book.

		Example:
			[{
				name: "Electric Boogaloo",
				title: "Breakin' 2: Electric Boogaloo"
				file: "b2eboogaloo.epub"
				chapters: [{
					name: "Chapter 1",
					link: "http://book.com/ch1"
				}]
			}]
		"""
		
		raise NotImplementedError
	
	@staticmethod
	def get_chapter_data(chapter):
		"""
		Add the content and metadata of a chapter to the given dictionary.
		
		At the end of this method, the chapter dict  must have at least the following keys:
		
		content -- an lxml html tree representing the text of the chapter, to be copied fully into another file.
		date ----- the string date that the chapter was published.
		
		Example:
			{
				name: "Foo",
				content: lxml.html("<p>Bar.</p><p>Baz!</p>"),
				date: "January 01, 1970"
			}
		"""
		
		raise NotImplementedError

