import socket
import objects
import xstruct

_continue = []

class Connection:
	def __init__(self, host, port=6923, nb=0, debug=0):
		self.host = host
		self.port = port

        	self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        self.s.connect((host, port))

		self.no = 0

		self.setblocking(nb)

		if debug:
			self.debug = debug

	def setblocking(self, nb):
		"""\
		Sets the connection to either blocking or non-blocking.
		"""
		if nb == 0 and self._noblock():
			# Check we arn't waiting on anything
			if len(self.nb) > 0:
				raise IOError("Still waiting on non-blocking commands!")
				
			self.s.setblocking(1)
			del self.nb

		elif nb == 1 and not self._noblock():
			self.s.setblocking(0)
			self.nb = []

	def poll(self):
		"""\
		Checks to see if a command can complete.
		"""
		if not self._noblock():
			raise IOError("Not a non-blocking connection!")
			
		if len(self.nb) == 0:
			return None

		ret = _continue
		while ret == _continue:
			ret = apply(self.nb[0][0], self.nb[0][1])
			if ret != None:
				self.nb.pop(0)
		
		return ret

	def _push(self, function, *args):
		"""\
		*Internal*

		Queues a fuction for polling.
		"""
		self.nb.append((function, args))

	def _pop(self):
		"""\
		*Internal*

		Removes the top of the queue.
		"""
		if self._noblock():
			self.nb.pop(0)

	def _noblock(self):
		"""\
		*Internal*

		Returns if the connection is polling.
		"""
		return hasattr(self, 'nb')

	def _send(self, p):
		"""\
		*Internal*

		Sends a single TP packet to the socket.
		"""
		s = self.s.send
		s(repr(p))

	def _recv(self):
		"""\
		*Internal*
		
		Reads a single TP packet from the socket.
		"""
		r = self.s.recv
		s = objects.Header.size
		
		h = r(s, socket.MSG_PEEK)

		if len(h) == s:
			p = objects.Header(h)

			if p.length > 0:
				d = r(s+p.length, socket.MSG_PEEK)
			
				if len(d) == s+p.length:
					p.process(d[s:])
				
					# Remove the stuff from the buffer
					r(s+p.length)
				
					return p
		return None

	def _common(self):
		"""\
		*Internal*

		Does all the common goodness.
		"""
		# Increase the no number
		self.no += 1

	def connect(self):
		"""\
		Connects to a Thousand Parsec Server.
		"""
		self._common()
		
		# Send a connect packet
		p = objects.Connect(self.no, "py-netlib/0.1")
		self._send(p)
		
		if self._noblock():
			self._push(self._connect, self.no)
			return None
		
		# and wait for a response
		return self._connect(self.no)
	
	def _connect(self, no):
		"""\
		*Internal*

		Completes the connect function.
		"""
		p = self._recv()
		if not p:
			return None

		# Check the sequence numbers match
		if p.sequence != no:
			raise IOError("Sequence numbers don't match\nRequired: %r Got: %r" % (no, p.sequence))

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def login(self, username, password):
		"""\
		Login to the server using this username/password.
		"""
		self._common()
		
		p = objects.Login(self.no, username, password)
		self._send(p)
		
		if self._noblock():
			self._push(self._login, self.no)
			return None
		
		# and wait for a response
		return self._login(self.no)
	
	def _login(self, no):
		"""\
		*Internal*

		Completes the login function.
		"""
		p = self._recv()
		if not p:
			return None

		# Check the sequence numbers match
		if p.sequence != no:
			raise IOError("Sequence numbers don't match\nRequired: %i Got: %i" % (no, p.sequence))

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def get_objects(self, a=None, y=None, z=None, r=None, x=None, id=None, ids=None):
		"""\
		Get objects from the server,

		# Get the object with id=25
		obj = get_objects(25)
		obj = get_objects(id=25)
		obj = get_objects(ids=[25])
		obj = get_objects([id])
		
		# Get the objects with ids=25, 36
		obj = get_objects([25, 36])
		obj = get_objects(ids=[25, 36])

		# Get the objects by position
		obj = get_objects(x, y, z, radius)
		obj = get_objects(x=x, y=y, z=z, r=radius)
		"""
		self._common()

		# Setup arguments
		if a != None and y != None and z != None and r != None:
			x = a
		
		if id != None:
			ids = [id]
		if a != None and not (y != None and z != None and r != None):
			ids = [a]
		if hasattr(a, '__getitem__'):
			ids = a
	
		p = None

		# Get by position mode
		if x != None:
			p = objects.Object_GetByPos(self.no, x, y, z, r)
		# Get by id mode
		if ids != None:
			p = objects.Object_GetById(self.no, ids)

		self._send(p)

		if self._noblock():
			self._push(self._get_objects_header, self.no)
			return None
		
		# and wait for a response
		return self._get_objects_header(self.no)

	def _get_objects_header(self, no):
		"""\
		*Internal*

		Completes the get_objects function.
		"""
		p = self._recv()
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.Fail):
			return False, p.s
		elif not isinstance(p, objects.Sequence):
			# We got a bad packet
			raise IOError("Bad Packet was received")

		self.store = []
		
		if self._noblock():
			for i in range(0, p.number):
				self._push(self._get_objects_data, self.no)

			self._push(self._get_objects_finish)

			# Keep the polling going
			return _continue

		for i in range(0, p.number):
			self._get_objects_data(self.no)
			
		return self._get_objects_finish()

	def _get_objects_data(self, no):
		"""\
		*Internal*

		Completes the get_objects function.
		"""
		p = self._recv()
		if p and isinstance(p, objects.Object):
			self.store.append(p)

			if self._noblock():
				return _continue

	def _get_objects_finish(self):
		"""\
		*Internal*

		Completes the get_objects function.
		"""
		store = self.store
		del self.store

		return store

	def disconnect(self):
		"""\
		Disconnect from a server.
		"""
		if self._noblock() and len(self.nb) > 0:
			raise IOError("Still waiting on non-blocking commands!")

		self.s.close()
		del self

"""\
>>> # Create the object and connect to the server
>>> c = netlib.Connection("127.0.0.1", 6329)
>>> if not c.connect():
>>>    print "Could not connect to the server"
>>>    sys.exit(1)
>>>
>>> if not c.login("username", "password"):
>>> 	print "Could not login"
>>> 	sys.exit(1)
>>>
>>> c.disconnect()
>>>

Non-Blocking Example Usage:

>>>
>>> import sys
>>>
>>> from tp import netlib
>>>
>>> # Create the object and connect to the server
>>> c = netlib.Connection("127.0.0.1", 6329, nb=1)
>>>
>>> c.connect()
>>> c.login("username", "password")
>>>
>>> # Wait for the connection to be complete
>>> if not c.wait():
>>>    print "Could not connect to the server"
>>>    sys.exit(1)
>>>
>>> r = c.poll()
>>> while r == None:
>>> 	r = c.poll()
>>>
>>> 	# Do some other stuff!
>>> 	pass
>>>
>>> if not r:
>>> 	print "Could not login"
>>> 	sys.exit(1)
>>>
>>> # Disconnect and cleanup
>>> c.disconnect()
>>>
"""
