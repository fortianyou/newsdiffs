from baseparser import BaseParser
from baseparser import day_diff2now
import re
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
#from BeautifulSoup import BeautifulSoup, Tag

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class CortanaParser(BaseParser):
    dynamic_loading = True
    domains = ['social.technet.microsoft.com', 'blogs.technet.microsoft.com']
    feeder_pat   = '^https?://blogs.technet.microsoft.com/machinelearning/(20[0-9]{2}/[0-9]{2})/.*'
    feeder_pages = ['https://social.technet.microsoft.com/Profile/Cortana%2bIntelligence%2band%2bML%2bBlog%2bTeam/activity']

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
        [x.extract() for x in soup.findAll('script')]

        self.real_article = True
        if soup.title != None: self.title = soup.title.string
                     
        div = soup.find('div', class_='entry-content') 
        if div == None:
            div = soup.find('div', id='Activities')
        if div != None:
            self.body = "\n".join([p.getText().strip() for p in 
            div.childGenerator() if isinstance(p, Tag)])
