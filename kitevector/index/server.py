import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import numpy as np
import pickle
import hnswlib
from kite import kite
from kite.xrg import xrg
from functools import partial
import argparse
import threading

class KiteIndex:

	indexes = {}
	idxlocks = {}

	@classmethod
	def get_lock(cls, idxname):
		if cls.idxlocks.get(idxname) == None:
			cls.idxlocks[idxname] = threading.Lock()
		return cls.idxlocks[idxname]

	@classmethod
	def load(cls, datadir):
		
		idxlist = ['movieindex_0_3', 'movieindex_1_3', 'movieindex_2_3']
		for idx in idxlist:
			with cls.get_lock(idx):
				print("KiteIndex.load")
				# load the index inside the lock

	@classmethod
	def query(cls, req):	
		idx = None
		idxname = '{}_{}_{}'.format(req['name'], req['fragment'][0], req['fragment'][1])
		print(idxname)
		with cls.get_lock(idxname):
			idx = cls.indexes[idxname]

		# found the index and get the nbest
		print("KiteIndex.query")

	@classmethod
	def create(cls, req):
		print("KiteIndex.create")
		idxname = '{}_{}_{}'.format(req['name'], req['fragment'][0], req['fragment'][1])
		with cls.get_lock(idxname):
			# create index inside the lock
			pass

	@classmethod
	def delete(cls, req):
		print("KiteIndex.delete")
	
class RequestHandler(BaseHTTPRequestHandler):

	def __init__(self, datadir, kite_port, *args, **kwargs):
		self.datadir = datadir
		self.kite_port = kite_port
		super().__init__(*args, **kwargs)

	def create_index(self):
		content_length = int(self.headers.get("Content-Length"))
		body = self.rfile.read(content_length)
		print(str(body))

		KiteIndex.create(json.loads(body))

		print(self.datadir)
		status = {'status': 'ok'}
		msg = json.dumps(status).encode('utf-8')
		
		self.send_response(200)
		self.send_header("Content-Length", len(msg))
		self.send_header("Content-Type", "application/json")
		self.end_headers()

		self.wfile.write(msg)

	def query(self):
		content_length = int(self.headers.get("Content-Length"))
		body = self.rfile.read(content_length)
		print(str(body))

		try:
			KiteIndex.query(json.loads(body))

			msg=b'''[[0.3, 1], [0.4, 2]]'''

			self.send_response(200)
			self.send_header("Content-Length", len(msg))
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(msg)
		except KeyError as e1:
			print('KeyError: ', e1)
			self.send_response(402)
			status = b'''{'status': 'error'}'''
			self.wfile.write(status)
		except Exception as e2:
			print(e2)
			self.send_response(402)
			status = b'''{'status': 'error'}'''
			self.wfile.write(status)
			

	
	def do_DELETE(self):
		if self.path == '/delete':
			self.delete_index()

	def do_POST(self):
		print("path = " , self.path)

		if self.path == '/create':
			self.create_index()
		elif self.path == '/query':
			self.query()
		else:
			pass



def run(args):
	server = ('', args.port)
	handler = partial(RequestHandler, args.datadir, args.kite)
	httpd = HTTPServer(server, handler)
	httpd.serve_forever()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', type=int, default=8181)
	parser.add_argument('--kite', type=int, default=7878)
	parser.add_argument('datadir')
	args = parser.parse_args()

	if not os.path.isdir(args.datadir):
		raise Exception("data directory not exists")

	run(args)
