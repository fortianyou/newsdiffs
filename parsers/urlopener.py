import urllib2
import socket
import time

class UrlOpener():
    def __init__(self):
        self._opener = urllib2.build_opener() 

    def get_html(self, url, max_depth=1):
        retry = False
        try:
            text = self._opener.open(url, timeout=5).read()
        except socket.timeout:
            retry = True
        except: 
            retry = True
        if retry:
            if max_depth == 0:
                raise Exception('Too many attempts to download %s' % url)
            time.sleep(0.5)
            return self.get_html(url, max_depth-1)
        return text