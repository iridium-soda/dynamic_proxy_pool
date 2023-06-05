"""
To maintain proxies via https://www.juliangip.com; provides interfaces to server
"""
import os

KEY = "./key.json"


class proxypool(object):
    def __init__(self):
        """
        Read config and Initialize data
        """
        self.poolsize = os.cpu_count()
        # size is equal to the maxium number of threads to run simultaneously  or maybe larger?
        
        with open(KEY, "r") as k:
            sec = k.read()
            url = sec["link"]
            k.close()
        self.pool = dict()  # Main proxy pool. Must be sorted when changing it.
