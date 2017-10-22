import cookielib
import logging
import re
import socket
import sys
import time
import urllib2
import string
from bs4 import SoupStrainer
import requests	
from datetime import datetime, timedelta

# Define a logger

# This formatter is like the default but uses a period rather than a comma
# to separate the milliseconds
class MyFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return logging.Formatter.formatTime(self, record,
                                            datefmt).replace(',', '.')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = MyFormatter('%(asctime)s:%(levelname)s:%(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)
logger.addHandler(ch)

def day_diff2now(url):
    last_modify_time = url_last_modified(url)
    if last_modify_time == None:
        return None 
    last_dt = datetime.strptime(last_modify_time, "%a, %d %b %Y %H:%M:%S %Z")
    cur_dt = datetime.now()
    date_diff = cur_dt - last_dt
    return date_diff.days

def url_last_modified(url):
    header = requests.head(url).headers
    if 'Last-Modified' in header:
        return header['Last-Modified']
    else:
        return None

def prepend_prefix(urls, domain):
    urls = [concat("http:", url) if url.startswith("//") else url for url in urls]
    # If no http://, prepend domain name
    urls = [url if '://' in url else concat(domain, url) for url in urls]
    return urls

def get_hrefs_by_soup(html):
    only_a_tags = SoupStrainer("a")
    soup = BeautifulSoup(html, "html.parser", parse_only=only_a_tags)
    urls = [a.get('href') or '' for a in soup.findAll('a')]
    return urls

def get_hrefs_by_regex(html):
    urls = re.findall('href="([^"]*)"', html) 
    return urls
 


def canonicalize_url(url):
    return url.split('?')[0].split('#')[0].strip().rstrip('/')

def filter_special_url(url):
    pattern = ".*\.(png|jpg|jpeg|css|xml|ico|/LICENSE)$"
    if re.match(pattern, url):
        return False 
    else:
        return True 

# Utility functions

def grab_url_use_retry(url, max_depth=1, opener=None):
    if opener is None:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    retry = False
    try:
        print "grab urls: %s" % url
        text = opener.open(url, timeout=5).read()
        if '<title>NY Times Advertisement</title>' in text:
            retry = True
    except socket.timeout:
        retry = True
    except: 
        retry = True
    if retry:
        if max_depth == 0:
            raise Exception('Too many attempts to download %s' % url)
        time.sleep(0.5)
        return grab_url_use_retry(url, max_depth-1, opener)
    return text

def grab_url(url, dynamic_loading=False):
    print "grab url %s" % url
    if dynamic_loading:
        return grab_dynamic_url(url)
    else:
        return grab_static_url(url)

import urlopener
url_opener = urlopener.UrlOpener()
def grab_static_url(url):
    return url_opener.get_html(url)

import phantom
phantom_opener = phantom.Phantom()
def grab_dynamic_url(url):
    text =  phantom_opener.get_html(url)
    return text

# Begin hot patch for https://bugs.launchpad.net/bugs/788986
# Ick.
from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulSoup
def bs_fixed_getText(self, separator=u""):
    bsmod = sys.modules[BeautifulSoup.__module__]
    if not len(self.contents):
        return u""
    stopNode = self._lastRecursiveChild().next
    strings = []
    current = self.contents[0]
    while current is not stopNode:
        if isinstance(current, bsmod.NavigableString):
            strings.append(current)
        current = current.next
    return separator.join(strings)
sys.modules[BeautifulSoup.__module__].Tag.getText = bs_fixed_getText
# End fix

def strip_whitespace(text):
    lines = text.split('\n')
    return '\n'.join(x.strip().rstrip(u'\xa0') for x in lines).strip() + '\n'

# from http://stackoverflow.com/questions/5842115/converting-a-string-which-contains-both-utf-8-encoded-bytestrings-and-codepoints
# Translate a unicode string containing utf8
def parse_double_utf8(txt):
    def parse(m):
        try:
            return m.group(0).encode('latin1').decode('utf8')
        except UnicodeDecodeError:
            return m.group(0)
    return re.sub(ur'[\xc2-\xf4][\x80-\xbf]+', parse, txt)

def canonicalize(text):
    return strip_whitespace(parse_double_utf8(text))

def concat(domain, url):
    return domain + url if url.startswith('/') else domain + '/' + url

# End utility functions

# Base Parser
# To create a new parser, subclass and define _parse(html).
class BaseParser(object):
    dynamic_loading = False
    url = None
    domains = [] # List of domains this should parse

    # These should be filled in by self._parse(html)
    date = None
    title = None
    byline = None
    body = None

    real_article = True # If set to False, ignore this article
    SUFFIX = ''         # append suffix, like '?fullpage=yes', to urls

    meta = []  # Currently unused.

    # Used when finding articles to parse
    feeder_pat   = None # Look for links matching this regular expression
    feeder_pages = []   # on these pages

    feeder_bs = BeautifulSoup #use this version of beautifulsoup for feed

    def __init__(self, url):
        self.url = url
        try:
            self.html = grab_url(self._printableurl(), self.dynamic_loading)
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.real_article = False
                return
            raise
        logger.debug('got html')
        self._parse(self.html)

    def _printableurl(self):
        url = self.url + self.SUFFIX
        return urllib2.quote(url.encode('utf-8'),safe=string.printable)
    #    return self.url + self.SUFFIX

    def _parse(self, html):
        """Should take html and populate self.(date, title, byline, body)

        If the article isn't valid, set self.real_article to False and return.
        """
        raise NotImplementedError()

    def __unicode__(self):
        if self.date == None: self.date = ''
        if self.title == None: self.title = ''
        if self.byline == None: self.byline = ''
        if self.body == None: self.body = ''
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                        self.body,)))

    @classmethod
    def filter(cls, url):
        raise NotImplementedError()

    @classmethod
    def feed_urls(cls):
        all_urls = set()
        seed_urls = cls.feeder_pages
        all_urls = all_urls | set([url for url 
        in map(canonicalize_url, seed_urls) if cls.filter(url)])
        
        while len(seed_urls) > 0:
            candidate_seeds = set()
            for feeder_url in seed_urls:
                try:
                    html = grab_url(feeder_url, cls.dynamic_loading)
                except:
                    continue

                domain = '/'.join(feeder_url.split('/')[:3])
                #soup = cls.feeder_bs(html, "lxml")

                urls = prepend_prefix(get_hrefs_by_soup(html), domain)
                # "or ''" to make None into str
                #urls = [a.get('href') or '' for a in soup.findAll('a')]
                legal_urls = map(canonicalize_url, urls)
                candidate_urls = [url for url in legal_urls if
                                   re.search(cls.feeder_pat, url)
                                    and filter_special_url(url) and cls.filter(url)]

                new_seeds = set(candidate_urls) - all_urls
                candidate_seeds = candidate_seeds | new_seeds
                all_urls = all_urls | set(candidate_urls)

            seed_urls = candidate_seeds
        return all_urls
