import os
from os.path import join
import tempfile
import re
import shutil
from uuid import uuid4
import zipfile

# http://www.idpf.org/epub/30/spec/epub30-ocf.html#sec-container-abstract-overview
# https://ebooks.stackexchange.com/questions/192/how-is-an-epub-structured-internally
# https://en.wikipedia.org/wiki/EPUB#Implementation

container_xml = "container.xml"


class EPub:
	# Content of boilerplate container file.
	container_text = """<?xml version="1.0" encoding="UTF-8"?>
	<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
		<rootfiles>
			<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
		</rootfiles>
	</container>
	"""
	
	content_template = """
	
	"""
	
	def __init__(self, title="", author=""):
		self.title = title
		self.author = author
		self.chapters = []
		self.tmpdir = tempfile.TemporaryDirectory() # Create the tmpdir
		self.main_dir = self.tmpdir.name
		self.content_dir = self.join_main("OEBPS")
		self.text_dir = self.join_content("text")
		
		# Make boilerplate files and dirs.
		with open(self.join_main("mimetype"), "w") as mime_file:
			mime_file.write("application/epub+zip")
		
		self.meta_inf = self.join_main("META-INF")
		os.mkdir(self.meta_inf)
		shutil.copy(container_xml, self.meta_inf)
		
		os.mkdir(self.content_dir)
		os.mkdir(self.text_dir)
		
	def add_chapter(self, ch_name, ch_text):
		filename = "a%s-%s.html" % (len(self.chapters)+1, str_to_filename(ch_name))
		with open(self.join_text(filename), "w") as ch_file:
			ch_file.write(ch_text)
		self.chapters.append((filename, ch_name))
	
	def set_cover(self, *lines):
		cover_text = "<div style='height:100%; width:100%; text-align:center'>"
		if len(lines) > 0:
			cover_text += "<h1 style='margin-top:35%;'>" + lines[0] + "</h1>"
		for line in lines[1:]:
			cover_text += "<h2 style='margin-top:10%;'>" + line + "</h2>"
		
		cover_text += "</div>"
		
		with open(self.join_content("cover.html"), "w") as cover:
			cover.write(cover_text)
	
	def output_file(self, filename):
		# Assemble chapter lists.
		content_manifest = "\n    ".join(["<item href=\"text/%s\" id=\"%s\" media-type=\"application/xhtml+xml\" />" %
										(ch_file, ch_file) for ch_file, ch_name in self.chapters])
		
		content_spine = "\n    ".join(["<itemref idref=\"%s\" />" % ch_file for ch_file, ch_name in self.chapters])
		
		nav = []
		it = 0
		for file, name in self.chapters:
			it += 1
			nav.append(("<navPoint id=\"navPoint-{it}\" playOrder=\"{it}\">"
						"<navLabel><text>{ch_name}</text></navLabel><content src=\"text/{ch_file}\" />"
						"</navPoint>").format(it=it, ch_name=name, ch_file=file))
		nav = "\n".join(nav)
		
		args = {"uuid": uuid4(), "title": self.title, "author": self.author}
		
		with open("content.opf.template") as content_tmpl:
			content_tmpl = content_tmpl.read().format(manifest=content_manifest, spine=content_spine, **args)
			with open(self.join_content("content.opf"), "w") as content:
				content.write(content_tmpl)
		
		with open("toc.ncx.template") as toc_tmpl:
			toc_tmpl = toc_tmpl.read().format(nav=nav, **args)
			with open(self.join_content("toc.ncx"), "w") as toc:
				toc.write(toc_tmpl)
		
		if not os.path.exists("out"):
			os.mkdir("out")
		with zipfile.ZipFile(join("out", filename), "w", compression=zipfile.ZIP_STORED) as book_file:
			book_file.write(self.join_main("mimetype"), arcname="mimetype", compress_type=zipfile.ZIP_STORED)
			book_file.write(join(self.meta_inf, container_xml), arcname=join("META-INF", container_xml))
			book_file.write(self.join_content("content.opf"), arcname=join("OEBPS", "content.opf"))
			book_file.write(self.join_content("toc.ncx"), arcname=join("OEBPS", "toc.ncx"))
			book_file.write(self.join_content("cover.html"), arcname=join("OEBPS", "cover.html"))
			
			for ch_file, ch_name in self.chapters:
				book_file.write(self.join_text(ch_file), arcname=join("OEBPS", "text", ch_file))
	
	def join_main(self, file):
		return join(self.main_dir, file)
	
	def join_content(self, file):
		return join(self.content_dir, file)
	
	def join_text(self, file):
		return join(self.text_dir, file)


def str_to_filename(string):
	return re.sub("[^-_.()[\]a-zA-Z0-9]", "-", string).strip("-").lower()


def s_words(words):
	"""
	Takes a word count and returns the word count shortened to thousands.
	e.g. 12345 -> 12.3
	"""
	
	return words // 100 / 10
