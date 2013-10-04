#!/usr/bin/env python2.6
# -*- encoding: utf-8 -*-

import BaseHTTPServer
import logging 
import os
import subprocess
import Cookie
import urlparse
import urllib, httplib, cgi
from suds.client import Client
from datetime import datetime
from urllib import url2pathname
from urllib2 import URLError
try:
    import simplejson as json
except ImportError:
    import json
import markup
import PXSPage
#-- local imports 
from EDServiceDescriptor import service_descriptor
from EDServiceDescriptor import postFunctionDict
from EDServiceDescriptor import getFunctionDict
from EDServiceDescriptor import sessionDict
from EDServiceDescriptor import masterSessionDict

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

	def __init__(self,request, client_address, server) :
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self,request, client_address, server)
		
	def do_GET(self):
		print("New GET req path:"+self.path)
		contentType = 'text/html'

		if 'Content-type' in self.headers:
			contentType = self.headers['Content-type']
			
		#-- gestion des requette http classique, 'fichier' , *.html, *.css, ...
		if (contentType == 'text/html'):
			docPath = "%s%s" % (self.server.docRoot, self.path)
			errorPath = "%s/not-found.html" % self.server.docRoot 
			unauthorisedPath = "%s/unauthorized.html" % self.server.docRoot 
			doc = ""
			if self.path.startswith('../'):
				code = 404
			elif docPath.endswith('/'):
				print("loading loadIndex()")
				doc = PXSPage.loadIndex()
				code = 200
			else:
				code = 404
			
			result = (code, doc, contentType)
		#-- gestion des requette ajax GET
		else:
			extractedpath = self.path.split('?')[0]
			so = self.Session()
			try:
				#-- appel au fcontion defini plus loin grace au dictionnaire 'getFunctionDict' cf EDServiceDescriptor.py
				#-- exemple : @service_descriptor("GET",5,"/ajax/search") 
				#--           la requete get pour l'url '/ajax/search' applera la fonction décorée
				#-- 		  le second parametre (5) donne les limitations en fonction du userpower cf EDServiceDescriptor.py et EDSessionElement.py
				#--					= 0 : fonction accessible en anonym
				#--					= 5 : user authentifier
				#--					> 5 : il faudra que le user soit trouvé dans la bdd avec un userpower > 5 (champs de la bdd)
				result = getFunctionDict[extractedpath](self,contentType,"",so)
			except KeyError, e:
				self.log_message("KeyError Error!"+str(e))
				result = (404,json.dumps({ "status": "Unhandeled request!" }),contentType)
			except EDPermitionException, e:
				self.log_message("Permition Error!"+str(e.value))
				result = (401,json.dumps({ "status": "e.value!" }),contentType)
			except EDMasterException, e:
				self.log_message("Master session list Error!"+str(e.value))
				result = (404,json.dumps({ "status": "e.value!" }),contentType)
		self.done(*result)
	
	#-- requete POST 
	def do_POST(self):
		print("New POST req path:"+self.path)
		#self.handle_data()
		
		contentLength = int(self.headers['Content-length'])
		content = self.rfile.read(contentLength)
		contentType = self.headers['Content-type']
		
		try:
			#-- appel au fcontion defini plus loin grace au dictionnaire 'postFunctionDict' cf EDServiceDescriptor.py
			#-- exemple : @service_descriptor("POST",5,"/ajax/search") 
			#--           la requete post pour l'url '/ajax/search' applera la fonction décoré 
			#-- 		  le second parametre (5) donne les limitations en fonction du userpower cf EDServiceDescriptor.py et EDSessionElement.py
			#--					= 0 : fonction accessible en anonym
			#--					= 5 : user authentifier
			#--					> 5 : il faudra que le user soit trouvé dans la bdd avec un userpower > 5 (champs de la bdd)
			result = postFunctionDict[self.path](self,contentType,content)
		except KeyError, e:
			self.log_message(e)
			result = (404,json.dumps({ "status": "Unhandeled request!" }),contentType)
		
		doc = PXSPage.loadIndex()
		self.done(*result)
	
	
	@service_descriptor("POST",0,"/servicelist")
	def servicelist(self,CntType,Cnt):
		print("servicelist() called")
		postvars = cgi.parse_qs(Cnt, keep_blank_values=1)
		print("postvars:"+str(postvars))
		print("    Calling methode.. exploring")
		url = "http://"+postvars["server"][0]+"/adxwsvc/services/CAdxWebServiceXmlCC?wsdl"
		try:
			client = Client(url)
			methodes = []
			for sd in client.sd :
				for port in sd.ports:
					for method in port[0].methods:
						methodes.append(str(method))
							
			
			CallContext = client.factory.create('CAdxCallContext')
			CallContext.codeLang = "FRA"
			CallContext.codeUser = postvars["user"]
			CallContext.password = postvars["pass"]
			CallContext.poolAlias = postvars["poolalias"]
			CallContext.poolId = None
			CallContext.requestConfig = None
			
			publicName = "AWE"
			objectKeys = client.factory.create('ArrayOfCAdxParamKeyValue')
			listSize = 100
			
			#-- appel au web service list objet AWE
			xmlWSLIST = client.service.query(CallContext,publicName,objectKeys,listSize)
			RetCnt = PXSPage.loadServicelist(methodes)
		except URLError as e:
			RetCnt = PXSPage.loadError(["URLError: can't reach server: "+url,"reason: "+str(e.reason)])
		CntType = 'text/html'
		return (202,RetCnt,CntType)
	
	
	@service_descriptor("POST",0,"/mainload")
	def mainload(self,CntType,Cnt):
		print("mainload() called")
		RetCnt = "you called mainload()"
		json_data = json.loads(Cnt)
		print("http://"+json_data["server"]+"/adxwsvc/services/CAdxWebServiceXmlCC?wsdl")
		#-- appel au eb service objet AWE pour liter les web services dispo
		req_params = self.buildSoapRequest("Query","AWE")
		req_headers = {"Content-type": "xml",
					   "SOAPAction":"Query"}
		conn = httplib.HTTPConnection(json_data["server"],timeout=1)
		conn.request("POST", "/adxwsvc/services/CAdxWebServiceXmlCC?wsdl", req_params, req_headers)
		response = conn.getresponse()
		print response.status, response.reason
		return (202,RetCnt,CntType)
	
	
	def buildSoapRequest(self,type,publicname):
		result = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"+\
				 "<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \n"+\
                 "          xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" \n"+\
                 "          xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n"+\
				 "<soap:Header >\n"+\
				 "</soap:Header>\n"+\
				 "<soap:Body>\n"+\
				 "<read xmlns=\"http://www.adonix.com/WSS\">\n"+\
				 "	<CAdxCallContext xmlns=\"http://www.adonix.com/WSS\">\n"+\
				 "		<codeLang type=\"XS:string\">FRA</codeLang>\n"+\
				 "		<codeUser type=\"XS:string\">WSERV</codeUser>\n"+\
				 "		<password type=\"XS:string\">9T4zDw6c</password>\n"+\
				 "		<poolAlias type=\"XS:string\">PARAMCE</poolAlias>\n"+\
				 "		<requestConfig type=\"XS:string\">adxwss.trace.on=off</requestConfig>\n"+\
				 "	</CAdxCallContext>\n"+\
				 "	<publicName>YBPC</publicName>\n"+\
				 "	<objectKeys arrayType=\"CAdxParamKeyValue[2]\"  xmlns:ns4=\"http://www.adonix.com/WSS\" >\n"+\
                 "		<key1 type=\"soapenc:Array\">\n"+\
                 "   		<key xmlns=\"http://www.adonix.com/WSS\">BPCNUM</key>\n"+\
                 "  		<value xmlns=\"http://www.adonix.com/WSS\">00003</value>\n"+\
                 "			</key1>\n"+\
				 "	</objectKeys>\n"+\
				 "	<listSize>999</listSize>\n"+\
				 "</read>\n"+\
				 "</soap:Body>\n"+\
				 "</soap:Envelope>\n";
		return result;

	
			
	def done(self, code, infile, contentType):
		#"""Send response, cookies, response headers 
		#and the data read from infile"""
		self.send_response(code)
		#for morsel in self.cookie.values():
			#log.debug('morsel.output : %s' % morsel.output)
		#	self.send_header('Set-Cookie', morsel.output(header='').lstrip())
		self.send_header("Content-type",contentType)
		self.end_headers()
		self.wfile.write(infile)
			
	
		
	def log_message(self, format, *args):
		log = logging.getLogger("logfun")
		
		#log.log(logging.DEBUG,"%s -- [%s] %s" %
        #                 (self.client_address[0],
        #                  self.log_date_time_string(),
        #                  format%args))
		
		