from baseparser import BaseParser
import re
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class TVMParser(BaseParser):
    domains = ['tvmlang.org']

    feeder_pat   = '^http://tvmlang.org'
    feeder_pages = ['http://tvmlang.org/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.real_article = True
        if soup.title != None: self.title = soup.title.string
        if soup.date != None: self.date = soup.time.string

        if soup.body != None:
            self.body = "\n".join([p.string for p in soup.body(text=True)])
