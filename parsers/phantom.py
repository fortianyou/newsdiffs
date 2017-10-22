from selenium import webdriver
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class Phantom():
  _driver = None
  def __init__(self):
    self._driver = webdriver.PhantomJS(THIS_DIR + '/phantomjs-2.1.1-macosx/bin/phantomjs')

  def __del__(self):
    self._driver.quit()
 
  def get_html(self, url):
    self._driver.get(url)
    if url.lower().rstrip('/') != self._driver.current_url.lower().rstrip('/'):
      msg = "input url is %s, but current url is %s" % (url, self._driver.current_url)
      print "[ERROR] %s" % msg
      raise Exception(msg)
  
    return self._driver.page_source
