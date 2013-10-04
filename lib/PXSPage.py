import markup
import sys, traceback


def loadIndex():
		page = markup.page( )
		page.init( css="( 'layout.css', 'alt.css', 'images.css' )" )
		page.div( class_='header' )
		page.h1("Soap Explorer")
		page.div.close( )
		page.div( class_='content' )
		page.h2("Service parameters")
		page.form(name_="input",method_="post",action_="servicelist")
		page.add("server:")
		page.input(id="server",type="text",name="server")
		page.br()
		page.add("user:")
		page.input(id="user",type="text",name="user")
		page.br()	
		page.add("pass:")
		page.input(id="pass",type="text",name="pass")
		page.br()
		page.input(type_="submit",value_="load",class_="load")
		page.form.close()
		page.div.close( )
		page.div( class_='footer' )
		page.p("footer")
		page.div.close( )
		return page
		
		
		
def loadServicelist():
		page = markup.page( )
		page.init( css="( 'layout.css', 'alt.css', 'images.css' )" )
		page.div( class_='header' )
		page.h1("Soap Explorer")
		page.div.close( )
		page.div( class_='content' )
		page.h2("Service List")
		page.div.close( )
		page.div( class_='footer' )
		page.p("footer")
		page.div.close( )
		return page
		
def loadError(msgs):
		page = markup.page( )
		page.init( css="( 'layout.css', 'alt.css', 'images.css' )" )
		page.div( class_='header' )
		page.h1("Soap Explorer")
		page.div.close( )
		page.div( class_='content' )
		page.h2("Error while execution request.")
		page.div( class_='error' )
		for msg in msgs:
			page.add(msg)
			page.br()
		page.div.close( )
		page.div.close( )
		
		page.div( class_='footer' )
		page.p("footer")
		page.div.close( )
		return page