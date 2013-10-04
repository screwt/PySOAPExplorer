#!/usr/bin/env python2.6
# -*- encoding: utf-8 -*-

#from EDException import EDPermitionException

#-- le decorateur ainsi defini permet de re-binder les fonctions de maniere plus claire cd handler.py (là ou il est utilisé)

#-- dictionary mapping function
postFunctionDict = {} 
#-- dictionary mapping function*
getFunctionDict = {} 
#-- dictionary mapping session id's to session objects
sessionDict = {} 
#-- dictionary mapping session id's to session objects
masterSessionDict = {} 

class service_descriptor(object):

	def __init__(self, type, powerRequired, path):
		#print "Inside __init__()"
		self.type = type
		self.path = path
		self.powerRequired = powerRequired

	def __call__(self, f):
		#print "Inside __call__()"
		def wrapped_f(*args):
			#print "Inside wrapped_f()"
			#print "Decorator arguments:", self.type , self.path, self.powerRequired
			#print("Necessary power:"+str(self.powerRequired)+" user power:"+str(args[3].userpower))
			#if(args[3].userpower<self.powerRequired):
			#	raise EDPermitionException("Error not enought power.")
			#else:
			return f(*args)
			#print "After f(*args)"

		wrapped_f.type = self.type
		wrapped_f.path = self.path
		wrapped_f.powerRequired = self.powerRequired		

		if (self.type=='POST'):
			postFunctionDict[self.path]=wrapped_f
		elif (self.type=='GET'):
			getFunctionDict[self.path]=wrapped_f
		
		return wrapped_f

