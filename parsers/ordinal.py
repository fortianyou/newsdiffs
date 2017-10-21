from baseparser import BaseParser
import re
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class OrdinalParser(BaseParser):
    domains = ['www.bigdatalab.ac.cn']

    feeder_pat   = '^https?://www.bigdatalab.ac.cn/~[(junxu)|(gjf)|(lanyanyan)]'
    feeder_pages = ['http://www.bigdatalab.ac.cn/~junxu/', 
    'http://www.bigdatalab.ac.cn/~gjf/',
    'http://www.bigdatalab.ac.cn/~lanyanyan/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.real_article = True
        if soup.title != None: self.title = soup.title.string
        if soup.date != None: self.date = soup.time.string

        if soup.body != None:
            self.body = "\n".join([p.string for p in soup.body(text=True)])
