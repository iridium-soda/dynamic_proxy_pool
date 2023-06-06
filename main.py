"""
Setup a server to listen requests from threads"""

import socket
import json
import logging
import os
import proxy

CONFIG="./cfg.json"
KEY="./key.json"
MAXIUMTHREADS=os.cpu_count()# How many requesets may be sent simultaneously
HOST=socket.gethostname()
PORT=7195
pp=proxy.proxypool()



def process_request(req:dict)->dict:
    """
    Process request and return response
    """
    try:
        resp=dict()
        if req["type"]=="get":
            addr=pp.extract_proxy()# A string like "ip:port"
            if not addr:
                logging.exception("Failed to get a vaild addr")
            resp["code"]=200
            resp["addr"]=addr
        elif req["type"]=="report": # Report the link is invaild
            pp.handle_error_report(req["addr"])
            addr=pp.extract_proxy()# A string like "ip:port"
            if not addr:
                logging.exception("Failed to get a vaild addr")
            resp["code"]=200
            resp["addr"]=addr
        
        
    except Exception as e:
        logging.exception(e)
        return dict()
    return resp
if __name__=="__main__":
    # Read config
    """
    with open(CONFIG, 'r') as cfg:
        cfg_data = json.load(cfg)
    try:
        # Read cfg
        
        port=cfg_data["port"]
    except Exception as e:
        logging.error("Failed to read config")
    """
    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()          
        while 1:
            conn, addr = s.accept()  
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024).decode('utf-8')  
                    if not data:
                        break
                    # data should be a dict here
                    data = json.loads(data)
                    response=process_request(data)
                    
                    conn.sendall(json.dumps(response).encode('utf-8'))  