"""
To maintain proxies via https://www.juliangip.com; provides interfaces to server
"""

import urllib.request
import json
import logging
import sys
from threading import Timer

KEY = "./key.json"
POOLSIZE=30
THRESHOLD=10 # when lifespan is less than threshold secs, remove the record from the pool

class proxypool(object):
    def __init__(self):
        """
        Read config and Initialize data
        """
        
        with open(KEY, "r") as k:
            sec = k.read()
            self.url = sec["link"]
            k.close()

        logging.info("Read url successfully")

        self.__init_pool()  # Main proxy pool. Must be sorted when changing it.

        self.poolsize=POOLSIZE # How many records the pool may contain.
        self.pool=[]
        # NOTE: A pool record should be like this:[ip,port,lifespan,True]

    def __init_pool(self)->None:
        """
        Initialize proxy pool structure
        """
        cnt=0
        while len(self.pool)<self.poolsize:
            self.pool+=self.__get_proxy_list()
            cnt+=1
            if cnt>=10: #Timeout to prevent deathloop
                logging.error("Unable to get proxy list and timeout. The server will exit")
                sys.exit()
        self.__sort()# Sort records by lifespan
        logging.info("Successfully initialize pool")

    def __sort(self)->None:
        """
        Sort pool by lifespan
        """
        self.pool.sort(key=lambda x: x[2], reverse=True)

    def __get_proxy_list(self)->list:
        """
        Get a proxy list from remote server.
        Error handler and killer timer should be included.
        Return: a list of records like [ip,port,lifespan] or err msg.
        """
        response = urllib.request.urlopen(self.url)   # Send request
        data = json.loads(response.read().decode())  # Parse JSON
        try:
            code=data["code"]
            if code !=200:
                # Error handle
                logging.warning("Get proxy from remote failed! Msg:",data["msg"])
                return []

            # Parse IP list
            count=data["count"]
            plist=data["proxy_list"]
            res=[]
            for r in plist:
                # Parse each list
                full_adress,lifespan=r.split(",")
                lifespan=int(lifespan)
                ip,port=full_adress.split(":")
                port=int(port)
                res.append([ip,port,lifespan,True])
            logging.info("Successfully add {} records to the pool",count)
            self.__kill_timer(res)
            logging.info("Kill timer ares set")
            return res
 
        except Exception as e:
            logging.warning("Get proxy list error:",e)
            return []

    def __kill_timer(self,recs:list)->None:
        """
        Remove records nearly die
        Set a timer after adding to the pool
        Imput: recs: a batch of records need to setup timer.
        """
        for r in recs:
            sTimer = Timer(r[-2]-THRESHOLD, self.__kill_record(r))# kill record when lifespan is less than threshold
            sTimer.start()

    def __kill_record(self,r:list)->None:
        """
        Remove the given single record from the pool
        """
        try:
            self.pool.remove(r)
        except Exception as e:
            logging.warning("Removing {} failed! {}",r,e)

    def extract_proxy(self)->set:
        """
        Extract a record for the client
        Return: a set like (ip:str,port:int)
        """
        while len(self.pool)<=POOLSIZE-10:
            # Add proxys until it's enough
            self.pool+=self.__get_proxy_list()
            
        self.__sort()

        for r in self.pool:
            if r[-1]:# this record is free
                r[-1]=False
                return (r[0],r[1])
        logging.warning("Unable to get an avaliable record")
        return (None,None)
    
    def handle_error_report(self,info:set)->None:
        """
        Remove records are reported unreachable
        Input: (ip,port)
        """
        for r in self.pool:
            if r[0]==info[0] and r[1]==info[1]:
                self.__kill_record(r)
                logging.info("Remove lost record {} successfully!",info)
                return 
            
        logging.warning("Unable to locate this lost record; check it again")
        return



