#!/usr/bin/env python2.6
# -*- encoding: utf-8 -*-
 
import BaseHTTPServer
import logging
import logging.handlers
import os
import re
import subprocess
import sys
import urllib2
import platform
from SocketServer import ThreadingMixIn
from datetime import date
#-- add the local libs folder
sys.path.append(os.getcwd()+"/lib/")
#-- local imports
import handler
#import Player2
#import Conf
#import EDLibrary
#from EDUtils import getch as getch


#-- base class
class AjaxServer(ThreadingMixIn,BaseHTTPServer.HTTPServer):
 
    def __init__(self, serverAddress, requestHandlerClass, docRoot,  upload):
		BaseHTTPServer.HTTPServer.__init__(self, serverAddress, requestHandlerClass)
		self.docRoot = docRoot
		self.uploadroot = upload
		
 
#-- from python module doc
def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler,
        root='root',
        ip='', 
		port=8000,
		upload=""):
 
    server_address = (ip, port)
    httpd = server_class(server_address, handler_class, root,upload)
    log.info("ajaxserver: waiting for requests")
    httpd.serve_forever()
     

#-- main function
if __name__ == '__main__':
	x = logging.getLogger("logfun")
	x.setLevel(logging.DEBUG)
	h1 = logging.FileHandler("server.log")
	f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
	h1.setFormatter(f)
	h1.setLevel(logging.DEBUG)
	x.addHandler(h1)
	
	log = logging.getLogger("logfun")

		
	#-- default config values
	ip = '127.0.0.1'
	port = 7778
	docRoot = str(os.getcwd())+'/www'
	print "listening on :"+ip+":"+str(port)+"\n"
	
	try: 
		#-- start the server
		log.info("ajaxserver: starting HTTP server on %s:%d" %(ip, port))
		run(server_class=AjaxServer, handler_class=handler.Handler, ip=ip, port=port, root=docRoot)
		log.info("ajaxserver: terminating")
		
	except KeyboardInterrupt, k:
		log.info( "\r<<terminated by user, good bye!>>")
		log.info("aborted by user, terminating")
		
