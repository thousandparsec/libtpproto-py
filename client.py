# Python Imports
import socket

# Local imports
import xstruct
import objects
constants = objects.constants

from common import Connection

class ClientConnection(Connection):
	"""\
	Class for a connection from the client side.
	"""

	def __init__(self, host=None, port=6923, nb=0, debug=0):
		Connection.__init__(self)

		self.buffers['undescribed'] = {}
		self.buffers['store'] = {}

		if host != None:
			self.setup(host, port, nb, debug)

	def setup(self, host, port=6923, nb=0, debug=0):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		self.host = host
		self.port = port

		s = None
		for af, socktype, proto, cannoname, sa in \
				socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):

			try:
				s = socket.socket(af, socktype, proto)
				if debug:
					print "Trying to connect to connect: (%s, %s)" % (host, port)

				s.connect(sa)
				break
			except socket.error, msg:
				if debug:
					print "Connect fail: (%s, %s)" % (host, port)
				if s:
					s.close()
					
				s = None
				continue
		
		if not s:
			raise socket.error, msg

		Connection.setup(self, s, nb=nb, debug=debug)

		self.no = 1

	def _description_error(self, p):
		# The packet doesn't have a description yet!?
		d = self.buffers['undescribed']
		
		# Store the packet and wait for the description
		if not d.has_key(p.type):
			d[p.type] = []

		d[p.type].append(p)

		# Send a request for the description
		p = objects.OrderDesc_Get(self.no-1, [p.type])
		self._send(p)

		return None

	def _description(self, p):
		d = self.buffers['undescribed']
	
		# The client must have requested the packet
		if not d.has_key(p.id):
			return p
	
		# Register the desciption error
		p.register()
	
		# The connection requested the packet
		# We have a packet waiting to be described
		q = d[p.id].pop(0)
		
		if len(d[p.id]) == 0:
			del d[p.id]
	
		q.process(q._data)
		return q

	def _common(self):
		"""\
		*Internal*

		Does all the common goodness.
		"""
		# Increase the no number
		self.no += 1

	def _okfail(self, no):
		"""\
		*Internal*

		Completes the an ok or fail function.
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

	def connect(self, str=""):
		"""\
		Connects to a Thousand Parsec Server.
		"""
		self._common()
		
		# Send a connect packet
		p = objects.Connect(self.no, "py-netlib/0.0.2" + str)
		self._send(p)
		
		if self._noblock():
			self._append(self._okfail, self.no)
			return None
		
		# and wait for a response
		return self._okfail(self.no)
	
	def login(self, username, password):
		"""\
		Login to the server using this username/password.
		"""
		self._common()

		self.username = username

		p = objects.Login(self.no, username, password)
		self._send(p)
		
		if self._noblock():
			self._append(self._okfail, self.no)
			return None
		
		# and wait for a response
		return self._okfail(self.no)
	
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
		self.buffers['store'][no] = []
	
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

			self.buffers['store'][no].append(p)

			if self._noblock():
				return _continue

	def _get_finish(self, no):
		"""\
		*Internal*

		Completes the get_* functions.
		"""
		store = self.buffers['store'][no]
		del self.buffers['store'][no]

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
		obj = get_orders(2, slot=5)
		obj = get_orders(2, slots=[5])
		obj = get_orders(2, [5])
		
		# Get the orders in slots 5 and 10 from object 2
		obj = get_orders(2, [5, 10])
		obj = get_orders(2, slots=[5, 10])

		# Get all the orders from object 2
		obj = get_orders(2)
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
			self._append(self._okfail, self.no)
			return None
		
		# and wait for a response
		return self._okfail(self.no)
		
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
			slots = [kw['slot']]
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

	def get_orderdescs(self, *args, **kw):
		"""\
		Get order descriptions from the server. 
		
		Note: When the connection gets an order which hasn't yet been
		described it will automatically get an order description for that
		order, you don't need to do this manually.

		# Get the order description for type 5
		obj = get_orderdescs(5)
		obj = get_orderdescs(type=5)
		obj = get_orderdescs(types=[5])
		obj = get_orderdescs([5])
		
		# Get the order description for type 5 and 10
		obj = get_orderdescs([5, 10])
		obj = get_orderdescs(types=[5, 10])
		"""
		self._common()

		if kw.has_key('types'):
			slots = kw['types']
		elif kw.has_key('type'):
			slots = [kw['type']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			slots = args[0]
		else:
			slots = args

		p = objects.OrderDesc_Get(self.no, types)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.OrderDesc, self.no))
			return None
		else:
			return self._get_header(objects.OrderDesc, self.no)

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

	def get_boards(self, x=None, id=None, ids=None):
		"""\
		Get boards from the server,

		# Get the board with id=25
		obj = get_boards(25)
		obj = get_boards(id=25)
		obj = get_boards(ids=[25])
		obj = get_boards([id])
		
		# Get the boards with ids=25, 36
		obj = get_boards([25, 36])
		obj = get_boards(ids=[25, 36])
		"""
		self._common()

		# Setup arguments
		if id != None:
			ids = [id]
		if hasattr(x, '__getitem__'):
			ids = x
		elif x != None:
			ids = [x]
	
		p = objects.Board_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.Board, self.no))
			return None
		else:
			return self._get_header(objects.Board, self.no)

	def get_messages(self, bid, *args, **kw):
		"""\
		Get messages from an board,

		# Get the message in slot 5 from board 2
		obj = get_messages(2, 5)
		obj = get_messages(2, slot=5)
		obj = get_messages(2, slots=[5])
		obj = get_messages(2, [5])
		
		# Get the messages in slots 5 and 10 from board 2
		obj = get_messages(2, [5, 10])
		obj = get_messages(2, slots=[5, 10])

		# Get all the messages from board 2
		obj = get_messages(2)
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

		p = objects.Message_Get(self.no, bid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.Message, self.no))
			return None
		else:
			return self._get_header(objects.Message, self.no)

	def insert_message(self, bid, slot, message, *args, **kw):
		"""\
		Add a new message to an board.

		Forms are
		insert_message(bid, slot, [arguments for message])
		insert_message(bid, slot, [Message Object])
		"""
		self._common()
		
		o = None
		if isinstance(message, objects.Message) or isinstance(message, objects.Message_Insert):
			o = message
			o._type = objects.Message_Insert.no
			o.sequence = self.no
		else:	
			o = apply(objects.Message_Insert, (self.no, bid, slot, message,)+args, kw)
			
		self._send(o)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None
		
		# and wait for a response
		return self._okfail(self.no)
		
	def remove_messages(self, oid, *args, **kw):
		"""\
		Removes messages from an board,

		# Remove the message in slot 5 from board 2
		obj = remove_messages(2, 5)
		obj = remove_messages(2, slot=5)
		obj = remove_messages(2, slots=[5])
		obj = remove_messages(2, [5])
		
		# Remove the messages in slots 5 and 10 from board 2
		obj = remove_messages(2, [5, 10])
		obj = remove_messages(2, slots=[5, 10])
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

		p = objects.Message_Remove(self.no, oid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, (objects.OK, self.no))
			return None
		else:
			return self._get_header(objects.OK, self.no)

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
