To use, run the desired scrape module with python3.

If the serial that the module points at has multiple books, by default all books will be scraped. If you want to only
scrape particular books, add the book numbers as arguments, e.g. `./scrape_apgte.py 2 3` would scrape only the 2nd and
3rd books of A Practical Guide to Evil.


To add serials, make a scrape_<name> module, within it make a class that inherits from scraper.Scraper and
implements its unimplemented methods, and finally call YourScraperClass.scrape in an `if __name__ == "__main__"` block.
