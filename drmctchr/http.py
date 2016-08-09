import os
import signal
import threading

from config import *
from core import *

import tornado.web
import tornado.template
import tornado.ioloop
import tornado.httpserver

class TornadoWebServer(threading.Thread):

	server = None

	def __init__(self):
		threading.Thread.__init__(self)
		debug("http", "service start")

	def run(self):
		application = tornado.web.Application([
			(r'(.*)/$', IndexHandler,),
			(r'/(.*)$', StaticFileHandler, {'path': "."}),
		])
		server = tornado.httpserver.HTTPServer(application)
		debug("http", "serving on 0.0.0.0:%d ..." % 8000)
		server.listen(8000)
		tornado.ioloop.IOLoop.instance().start()

class IndexHandler(tornado.web.RequestHandler):
	SUPPORTED_METHODS = ['GET']

	def get(self, path):
		""" GET method to list contents of directory or
		write index page if index.html exists."""

		# remove heading slash
		path = path[1:]

		for index in ['index.html', 'index.htm']:
			index = os.path.join(path, index)
			if os.path.exists(index):
				with open(index, 'rb') as f:
					self.write(f.read())
					self.finish()
					return
		html = self.generate_index(path)
		self.write(html)
		self.finish()

	def generate_index(self, path):
		""" generate index html page, list all files and dirs.
		"""
		files = os.listdir(".")
		files = [filename + '/'
				if os.path.isdir(os.path.join(path, filename))
				else filename
				for filename in files]
		html_template = """
		<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.1 Final//EN"><html>
		<title>Directory listing for /{{ path }}</title>
		<body>
		<h2>Directory listing for /{{ path }}</h2>
		<hr>
		<ul>
		{% for filename in files %}
		<li><a href="{{ filename }}">{{ filename }}</a>
		{% end %}
		</ul>
		<hr>
		</body>
		</html>
		"""
		result = tornado.template.Template(html_template)
		return result.generate(files=files, path=path)

class StaticFileHandler(tornado.web.StaticFileHandler):
	def write(self, chunk):
		super(StaticFileHandler, self).write(chunk)
		self.flush()