from baseparser import BaseParser
from baseparser import day_diff2now
import re
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
#from BeautifulSoup import BeautifulSoup, Tag

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class GgBlogParser(BaseParser):
    domains = ['research.googleblog.com/']
    feeder_pat   = '^https?://research.googleblog.com/(20[0-9]{2}/[0-9]{2})/.*.html'
    feeder_pages = ['https://research.googleblog.com/']

    @classmethod
    def filter(cls, url):
        group = re.search(cls.feeder_pat, url)
        if group == None:
            return False
        [year, month] = group.group(1).split('/')
        cur_year = datetime.now().year
        if cur_year - int(year) > 1:
            return False 
        else:
            return True
            
    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser',
                             from_encoding='utf-8')
 
        self.real_article = True
        if soup.title != None: self.title = soup.title.string
        if soup.date != None: 
            self.date = soup.find('span', 
                                   attrs={'itemprop':'datePublished'}).get('content')
        soup.byline = soup.find('span', 
                                   attrs={'class':'byline-author'}).get('content')
                                   
        [x.extract() for x in soup.findAll('script')]

        div = soup.find('div', attrs={'itemprop':'articleBody'}) 
        if soup.body != None:
            self.body = "".join([p.getText().strip() for p in 
            div.childGenerator() if isinstance(p, Tag)])

