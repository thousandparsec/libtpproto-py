import socket

import objects
import xstruct

from support.output import *

from common import Connection
class ClientConnection(Connection):
	"""\
	Class for a connection from the client side.
	"""
	
	def __init__(self, host=None, port=6923, nb=0, debug=0):
		"""\
		"""
		if host != None:
			self.setup(host, port, nb, debug)

	def setup(self, host, port=6923, nb=0, debug=0):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		self.host = host
		self.port = port

		for af, socktype, proto, cannoname, sa in \
				socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):

			try:
				self.s = socket.socket(af, socktype, proto)
				if debug:
					print "Trying to connect to connect: (%s, %s)" % (host, port)

				self.s.connect(sa)
				break
			except socket.error, msg:
				if debug:
					print "Connect fail: (%s, %s)" % (host, port)
				if self.s:
					self.sock.close()
					
				self.s = None
				continue
		
		if not self.s:
			raise socket.error, msg

		self.no = 1
		self.setblocking(nb)

		self.debug = debug

		# This is a storage for out of sequence packets
		self.rbuffer = {}
		# Storage for frames which havn't got a description yet
		self.ubuffer = {}

		self.store = {}

	def _description_error(self, packet):
		# FIXME: Return an error if its a server connection?
		# The packet doesn't have a description yet!?

		# Store the packet and wait for the description
		if not d.has_key(p.type):
			d[p.type] = []

		d[p.type].append(p)

		# FIXME: Send a request for the description


	def _common(self):
		"""\
		*Internal*

		Does all the common goodness.
		"""
		# Increase the no number
		self.no += 1

	def connect(self, str=""):
		"""\
		Connects to a Thousand Parsec Server.
		"""
		self._common()
		
		# Send a connect packet
		p = objects.Connect(self.no, "py-netlib/0.0.2" + str)
		self._send(p)
		
		if self._noblock():
			self._append(self._connect, self.no)
			return None
		
		# and wait for a response
		return self._connect(self.no)
	
	def _connect(self, no):
		"""\
		*Internal*

		Completes the connect function.
		"""
		p = self._recv(no)
		if not p:
			return None

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

		self.username = username

		p = objects.Login(self.no, username, password)
		self._send(p)
		
		if self._noblock():
			self._append(self._login, self.no)
			return None
		
		# and wait for a response
		return self._login(self.no)
	
	def _login(self, no):
		"""\
		*Internal*

		Completes the login function.
		"""
		p = self._recv(no)
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")
	
	def _get_header(self, type, no):
		"""\
		*Internal*

		Completes the get_* function.
		"""
		p = self._recv(no)
		if not p:
			return None

		if isinstance(p, objects.Fail):
			# The whole command failed :(
			return False, p.s
		elif isinstance(p, type):
			# Must only be one, so return
			return p
		elif not isinstance(p, objects.Sequence):
			# We got a bad packet
			raise IOError("Bad Packet was received %s" % p)

		# We have to wait on multiple packets
		self.store[no] = []
	
		if self._noblock():
			# Do the commands in non-blocking mode
			self._next(self._get_finish, no)
			for i in range(0, p.number):
				self._next(self._get_data, (type, no))

			# Keep the polling going
			return _continue

		else:
			# Do the commands in blocking mode
			for i in range(0, p.number):
				self._get_data(type, no)
			
			return self._get_finish(no)

	def _get_data(self, type, no):
		"""\
		*Internal*

		Completes the get_* function.
		"""
		p = self._recv(no)

		if p != None:
			if isinstance(p, objects.Fail):
				p = (False, p.s)
			elif not isinstance(p, type):
				raise IOError("Bad Packet was received %s" % p)

			self.store[no].append(p)

			if self._noblock():
				return _continue

	def _get_finish(self, no):
		"""\
		*Internal*

		Completes the get_* functions.
		"""
		store = self.store[no]
		del self.store[no]

		return store

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
			self._append(self._get_header, (objects.Object, self.no))
			return None
		else:
			return self._get_header(objects.Object, self.no)

	def get_orders(self, oid, *args, **kw):
		"""\
		Get orders from an object,

		# Get the order in slot 5 from object 2
		obj = get_orders(2, 5)
		obj = get_objects(2, slot=5)
		obj = get_objects(2, slots=[5])
		obj = get_objects(2, [5])
		
		# Get the orders in slots 5 and 10 from object 2
		obj = get_objects(2, [5, 10])
		obj = get_objects(2, slots=[5, 10])

		# Get all the orders from object 2
		obj = get_objects(2)
		"""
		self._common()

		if kw.has_key('slots'):
			slots = kw['slots']
		elif kw.has_key('slot'):
			slots = [kw['slots']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			slots = args[0]
		else:
			slots = args

		p = objects.Order_Get(self.no, oid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.Order, self.no))
			return None
		else:
			return self._get_header(objects.Order, self.no)

	def insert_order(self, oid, slot, type, *args, **kw):
		"""\
		Add a new order to an object.

		Forms are
		insert_order(oid, slot, type, [arguments for order])
		insert_order(oid, slot, [Order Object])
		"""
		self._common()
		
		o = None
		if isinstance(type, objects.Order) or isinstance(type, objects.Order_Insert):
			o = type
			o._type = objects.Order_Insert.no
			o.sequence = self.no
		else:	
			o = apply(objects.Order_Insert, (self.no, oid, slot, type,)+args, kw)
			
		self._send(o)

		if self._noblock():
			self._append(self._insert_order, self.no)
			return None
		
		# and wait for a response
		return self._insert_order(self.no)
		
	def _insert_order(self, no):
		"""\
		*Internal*

		Completes the insert order function.
		"""
		p = self._recv(no)
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def remove_orders(self, oid, *args, **kw):
		"""\
		Removes orders from an object,

		# Remove the order in slot 5 from object 2
		obj = remove_orders(2, 5)
		obj = remove_objects(2, slot=5)
		obj = remove_objects(2, slots=[5])
		obj = remove_objects(2, [5])
		
		# Remove the orders in slots 5 and 10 from object 2
		obj = remove_objects(2, [5, 10])
		obj = remove_objects(2, slots=[5, 10])
		"""
		self._common()

		if kw.has_key('slots'):
			slots = kw['slots']
		elif kw.has_key('slot'):
			slots = [kw['slots']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			slots = args[0]
		else:
			slots = args

		p = objects.Order_Remove(self.no, oid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.OK, self.no))
			return None
		else:
			return self._get_header(objects.OK, self.no)

	def time(self):
		"""\
		Connects to a Thousand Parsec Server.
		"""
		self._common()
		
		# Send a connect packet
		p = objects.TimeRemaining_Get(self.no)
		self._send(p)
		
		if self._noblock():
			self._append(self._time, self.no)
			return None
		
		# and wait for a response
		return self._time(self.no)
	
	def _time(self, no):
		"""\
		*Internal*

		Completes the time function.
		"""
		p = self._recv(no)
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.TimeRemaining):
			return True, p.time
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

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
