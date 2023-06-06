"""
To maintain proxies via https://www.juliangip.com; provides interfaces to server
"""

import urllib.request
import json
import logging
import sys
from threading import Timer
import schedule

KEY = "./key.json"
POOLSIZE=30
THRESHOLD=10 # when lifespan is less than threshold secs, remove the record from the pool

class proxypool(object):
    def __init__(self):
        """
        Read config and Initialize data
        """
        
        with open(KEY, "r") as k:
            # Read linkss
            sec = json.load(k)
            self.url = sec["extract_link"]
            self.check=sec["check_link"]
            k.close()

        logging.info("Read url successfully")
        self.poolsize=POOLSIZE # How many records the pool may contain.
        self.pool=[]
        # NOTE: A pool record should be like this:["ip:port",lifespan]
        self.__refill() #Initializde pool
        schedule.every(1).seconds.do(self.monitor())# Start monitor

    def __refill(self)->None:
        """
        To refill the pool to the size
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
        self.pool.sort(key=lambda x: x[-1], reverse=True)

    def __get_proxy_list(self)->list:
        """
        Get a proxy list from remote server.
        Error handler and killer timer should be included.
        Return: a list of records like ["ip:port",lifespan] or err msg.
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
            count=data["data"]["count"]
            plist=data["data"]["proxy_list"]
            res=[]
            for r in plist:
                # Parse each list
                full_adress,lifespan=r.split(",")
                lifespan=int(lifespan)
                res.append([full_adress,lifespan])
            logging.info("Successfully add {} records to the pool",count)
            #self.__kill_timer(res)
            #logging.info("Kill timer ares set")
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
            sTimer = Timer(r[-1]-THRESHOLD, self.__kill_record(r))# kill record when lifespan is less than threshold
            sTimer.start()

    def __kill_record(self,r:list)->None:
        """
        Remove the given single record from the pool
        """
        try:
            self.pool.remove(r)
        except Exception as e:
            logging.warning("Removing {} failed! {}",r,e)

    def extract_proxy(self)->str:
        """
        Extract a record for the client
        Return: a str like"ip:port"
        """
        self.__refill()

        try:
            ip=self.pool[0]
            return ip#Here should be "ip:port"
        except Exception as e:
            logging.warning("Unable to get an avaliable record")
            return ""
           
    def handle_error_report(self,ip:str)->None:
        """
        Remove records are reported unreachable
        Input: "ip:port"
        """
        for r in self.pool:
            if r[0]==ip:
                self.__kill_record(r)
                logging.info("Remove lost record {} successfully!",ip)
                return 
            
        logging.warning("Unable to locate this lost record; check it again")
        return

    def monitor(self)->None:
        """
        Check, kill and refill the pool per 1 sec
        """
        querystr=""
        for r in self.pool:
            querystr+=r[0].replace(":","%3A")# Combine query string
            querystr+="%2C"
        querystr=querystr[:-3]#turncate the final comma
        requeststr=self.check+querystr
        logging.info("Sending")
        response = urllib.request.urlopen(requeststr)   # Send request
        data = json.loads(response.read().decode())  # Parse JSON
        try:
            code=data["code"]
            if code !=200:
                # Error handle
                logging.warning("Check from remote failed! Msg:",data["msg"])
                return 
            respdict=data["data"]
            for addr in respdict:
                if not(respdict[addr]):
                    # The addr is unavaliable
                    for r in self.pool:
                        if r[0]==addr:
                            self.__kill_record(r)
                            logging.info("Killing {} as it is invaild now.",addr)
            # refill the pool
            self.__refill()
            
        except Exception as e:
            logging.exception(e)
        

