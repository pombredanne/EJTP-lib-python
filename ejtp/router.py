'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''


'''
	EJTP Router.

	This virtual device takes jacks on one side for external communication,
	and clients on the other side for internal frame routing.
'''

from frame import Frame
from ejtp.util.crashnicely import Guard

class Router(object):
	def __init__(self, jacks=[], clients=[]):
		self.runstate = "stopped"
		self._jacks = {}
		self._clients = {}
		self._loadjacks(jacks)
		self._loadclients(clients)
		self.logging = True
		self.log = []
		self.run()

	def recv(self, msg):
		# Accepts string or frame.frame
		#print "\nRouter incoming frame: "+repr(str(msg))
		self.log_add(msg)
		try:
			msg = Frame(msg)
		except Exception as e:
			print "Router could not parse frame:", repr(msg)
			print e
			return
		if msg.type == "r":
			recvr = self.client(msg.addr) or self.jack(msg.addr)
			if recvr:
				with Guard():
					recvr.route(msg)
			else:
				print "Router could not deliver frame:", str(msg.addr)
		elif msg.type == "s":
			print "frame recieved directly from "+str(msg.addr)

	def jack(self, addr):
		# Return jack registered at addr, or None
		for (t, l) in self._jacks:
			if t == addr[0]:
				return self._jacks[(t,l)]
		return None

	def client(self, addr):
		# Return client registered at addr, or None
		addr = rtuple(addr[:3])
		if addr in self._clients:
			return self._clients[addr]
		else:
			return None

	def log_add(self, msg):
		if self.logging:
			self.log.append(str(msg))

	def log_dump(self):
		print "["
		print ",\n".join([" "*4+repr(x) for x in self.log])
		print "]"

	def thread_all(self):
		# Run all Jack threads
		for i in self._jacks:
			self._jacks[i].run_threaded()

	def stop_all(self):
		# Run all Jack threads
		for i in self._jacks:
			self._jacks[i].close()

	def run(self, level="threaded"):
		if level=="threaded":
			if self.runstate == "stopped":
				self.thread_all()
		elif level=="stopped":
			# stop all jacks
			self.stop_all()
		self.runstate = level

	def _loadjacks(self, jacks):
		for j in jacks:
			self._loadjack(j)

	def _loadclients(self, clients):
		for c in clients:
			self._loadclient(c)

	def _loadjack(self, jack):
		key = rtuple(jack.interface[:2])
		self._jacks[key] = jack
		if self.runstate == "threaded":
			jack.run_threaded()

	def _loadclient(self, client):
		key = rtuple(client.interface[:3])
		self._clients[key] = client

def rtuple(obj):
	# Convert lists into tuples recursively
	if type(obj) in (list, tuple):
		return tuple([rtuple(i) for i in obj])
	else:
		return obj
