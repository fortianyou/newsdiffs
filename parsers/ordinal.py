from baseparser import BaseParser
from baseparser import day_diff2now
import re
from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class OrdinalParser(BaseParser):
    domains = ['www.bigdatalab.ac.cn']

    feeder_pat   = '^https?://www.bigdatalab.ac.cn/~[(junxu)|(gjf)|(lanyanyan)]'
    feeder_pages = ['http://www.bigdatalab.ac.cn/~junxu/', 
    'http://www.bigdatalab.ac.cn/~gjf/',
    'http://www.bigdatalab.ac.cn/~lanyanyan/']

    @classmethod
    def filter(cls, url):
        day_diff = day_diff2now(url)
        if day_diff == None or day_diff < 365 * 2:
            return True 
        else:
            return False 
 
    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser',
                             from_encoding='utf-8')
        self.real_article = True
        if soup.title != None: self.title = soup.title.string
        if soup.date != None: self.date = soup.time.string

        if soup.body != None:
            self.body = "\n".join([p.string for p in soup.body(text=True)])
