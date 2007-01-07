"""\
This module contains the client based connections.

Blocking Example Usage:

>>> # Create the object and connect to the server
>>> c = netlib.Connection("127.0.0.1", 6329)
>>> if failed(c.connect()):
>>>    print "Could not connect to the server"
>>>    sys.exit(1)
>>>
>>> if failed(c.login("username", "password")):
>>> 	print "Could not login"
>>> 	sys.exit(1)
>>>
>>> c.disconnect()
>>>

Non-Blocking Example Usage:

>>> # Create the object and connect to the server
>>> c = netlib.Connection("127.0.0.1", 6329, nb=1)
>>>
>>> c.connect()
>>> c.login("username", "password")
>>>
>>> # Wait for the connection to be complete
>>> if failed(c.wait()):
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
>>> if failed(r):
>>> 	print "Could not login"
>>> 	sys.exit(1)
>>>
>>> # Disconnect and cleanup
>>> c.disconnect()
>>>
"""

# Python Imports
import encodings.idna
import re
import socket
import types
import urllib

# Local imports
import xstruct
import objects
constants = objects.constants

from version import version
from common import Connection, l, SSLWrapper, _continue

def failed(object):
	if type(object) == types.TupleType:
		return failed(object[0])
	else:
		if isinstance(object, objects.Fail):
			return True
		if isinstance(object, bool):
			return not object
	return False

sequence_max = 4294967296

def url2bits(line):
	urlspliter = r'(.*?://)?(((.*):(.*)@)|(.*)@)?(.*?)(:(.*?))?(/.*?)?$'
	groups = re.compile(urlspliter, re.M).search(line).groups()
	
	proto = groups[0]

	if not groups[3] is None:
		username = groups[3]
	elif not groups[5] is None:
		username = groups[5]
	else:
		username = None

	server = groups[6]
	port = groups[8]

	password = groups[4]
	if not password is None:
		if password[-1] is '@':
			password = password[:-1]

	game = groups[9]
	if not game is None:
		game = urllib.unquote_plus(game)
		if game[0] == '/':
			game = game[1:]
		if len(game) == 0:
			game = None

	if proto is None:
		one = server
	else:
		one = "%s%s" % (proto, server)

	if not port is None:
		one = "%s:%s" % (one, port)

	return (one, username, game, password)


class ClientConnection(Connection):
	"""\
	Class for a connection from the client side.
	"""

	def __init__(self, host=None, port=None, nb=0, debug=0):
		Connection.__init__(self)

		self.buffered['undescribed'] = {}
		self.buffered['store'] = {}

		if host != None:
			self.setup(host, port, nb, debug)

		self.__desc = False

	def setup(self, host, port=None, nb=0, debug=0, proxy=None):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		hoststring = host
		self.proxy = None
		
		if hoststring.startswith("tphttp://") or hoststring.startswith("tphttps://"):
			hoststring = hoststring[2:]

		if hoststring.startswith("http://") or hoststring.startswith("https://"):
			import urllib
			opener = None

			# use enviroment varibles
			if proxy == None:
				opener = urllib.FancyURLopener()
			elif proxy == "":
				# Don't use any proxies
				opener = urllib.FancyURLopener({})
			else:
				if hoststring.startswith("http://"):
					opener = urlib.FancyURLopener({'http': proxy})
				elif hoststring.startswith("https://"):
					opener = urlib.FancyURLopener({'https': proxy})
				else:
					raise "URL Error..."

			import random, string
			url = "/"
			for i in range(0, 12):
				url += random.choice(string.letters+string.digits)

			o = opener.open(hoststring + url, "")
			s = socket.fromfd(o.fileno(), socket.AF_INET, socket.SOCK_STREAM)

##			# Read in the headers
##			buffer = ""
##			while not buffer.endswith("\r\n\r\n"):
##				print "buffer:", repr(buffer)
##				try:
##					buffer += s.recv(1)
##				except socket.error, e:
##					pass
##			print "Finished the http headers..."

		else:
			if hoststring.startswith("tp://") or hoststring.startswith("tps://"):
				if hoststring.startswith("tp://"):
					host = hoststring[5:]
					if not port:
						port = 6923
				elif hoststring.startswith("tps://"):
					host = hoststring[6:]
					if not port:
						port = 6924

				if host.count(":") > 0:
					host, port = host.split(':', 1)
					port = int(port)
			else:
				if hoststring.count(":") > 0:
					host, port = hoststring.split(':', 1)
					port = int(port)
				else:
					host = hoststring

					if not port:
						port = 6923

			print "Connecting to", host, type(host), port, type(port)

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

			if hoststring.startswith("tps://"):
				s = SSLWrapper(s)

		self.hoststring = hoststring
		self.host = host
		self.port = port

		Connection.setup(self, s, nb=nb, debug=debug)
		self.no = 1

	def _description_error(self, p):
		# Need to figure out how to do non-blocking properly...
		# Send a request for the description
		if not self.__desc:
			q = objects.OrderDesc_Get(p.sequence-1, [p.type])
			self._send(q)

			self.__desc = True

		q = self._recv(p.sequence-1)

		if q != None and isinstance(q, objects.Sequence):
			q = self._recv(p.sequence-1)

		if q != None and isinstance(q, objects.Description):
			self.__desc = False

			# Register the desciption
			q.register()

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

	def _get_single(self, type, no):
		"""\
		*Internal*

		Completes the function which only get a signle packet returned.
		"""
		p = self._recv(no)
		if not p:
			return None

		if isinstance(p, type):
			return p
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			raise IOError("Bad Pakcet was received")

	def _get_header(self, type, no, callback=None):
		"""\
		*Internal*

		Completes the get_* function.
		"""
		p = self._recv(no)
		if not p:
			return None

		if isinstance(p, objects.Fail):
			# The whole command failed :(
			return (False, p.s)
#			return [(False, p.s)]
		elif isinstance(p, type):
			# Must only be one, so return
			if not callback is None:
				callback(p)

			return [p]
		elif not isinstance(p, objects.Sequence):
			# We got a bad packet
			raise IOError("Bad Packet was received %s" % p)

		# We have to wait on multiple packets
		self.buffered['store'][no] = []

		#print "Packets to get", p.number

		if self._noblock():
			# Do the commands in non-blocking mode
			self._next(self._get_finish, no)
			for i in range(0, p.number):
				self._next(self._get_data, type, no, callback)

			# Keep the polling going
			return _continue

		else:
			# Do the commands in blocking mode
			for i in range(0, p.number):
				self._get_data(type, no, callback)

			return self._get_finish(no)

	def _get_data(self, type, no, callback=None):
		"""\
		*Internal*

		Completes the get_* function.
		"""
		p = self._recv(no)

		if p != None:
			if not callback is None:
				callback(p)

			if isinstance(p, objects.Fail):
				p = (False, p.s)
			elif not isinstance(p, type):
				raise IOError("Bad Packet was received %s" % p)

			self.buffered['store'][no].append(p)

			if self._noblock():
				return _continue

	def _get_finish(self, no):
		"""\
		*Internal*

		Completes the get_* functions.
		"""
		store = self.buffered['store'][no]
		del self.buffered['store'][no]
		return l(store)

	def _get_ids(self, type, key, position, amount=-1, raw=False):
		"""\
		*Internal*

		Send a GetID packet and setup for a IDSequence result.
		"""
		self._common()

		p = type(self.no, key, position, amount)
		self._send(p)

		if self._noblock():
			self._append(self._get_idsequence, self.no, False, raw)
			return None
		else:
			return self._get_idsequence(self.no, False, raw)

	def _get_idsequence(self, no, iter=False, raw=False):
		"""\
		*Internal*

		Finishes any function which gets an IDSequence.
		"""
		p = self._recv(no)
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.Fail):
			return False, p.s
		elif isinstance(p, objects.IDSequence):
			if iter:
				return p.iter()
			elif raw:
				return p
			else:
				return p.ids
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	class IDIter(object):
		"""\
		*Internal*

		Class used to iterate over an ID list. It will get more IDs as needed.

		On a non-blocking connection the IDIter will return (None, None) while
		no data is ready. This makes it good to use in an event loop.

		On a blocking connection the IDIter will wait till the information is
		ready.
		"""
		def __init__(self, connection, type, amount=30):
			"""\
			IDIter(connection, type, amount=10)

			connection
				Is a ClientConnection
			type
				Is the ID of the GetID packet to send
			amount
				Is the amount of IDs to get at one time
			"""
			self.connection = connection
			self.type = type
			self.amount = amount

			self.total = None

			self.key = None
			self.remaining = None

			self.position = None
			self.ids = None

			# Send out a packet if we are non-blocking
			if self.connection._noblock():
				self.next()

		def __iter__(self):
			return self

		def next(self):
			"""\
			Get the next (ids, modified time) pair.
			"""

			# Get the total number of IDs
			if self.key is None and self.remaining is None:
				if self.ids is None:
					self.ids = []
					p = self.connection._get_ids(self.type, -1, 0, 0, raw=True)
				else:
					p = self.connect.poll()

				# Check for Non-blocking mode
				if p is None:
					return (None, None)
				# Check for an error
				elif failed(p):
					raise IOError("Failed to get remaining IDs")

				if self.total == None:
					self.total = p.left

				self.remaining = p.left
				self.key = p.key
				self.position = 0

			# Get more IDs
			if len(self.ids) <= 0:
				no = self.remaining
				if no <= 0:
					raise StopIteration()
				elif no > self.amount:
					no = self.amount

				p = self.connection._get_ids(self.type, self.key, self.position, no, raw=True)
				# Check for Non-blocking mode
				if p is None:
					return (None, None)
				# Check for an error
				elif failed(p):
					raise IOError("Failed to get remaining IDs")

				self.ids = p.ids
				self.remaining = p.left

			self.position += 1
			return self.ids.pop(0)

	def connect(self, str=""):
		"""\
		Connects to a Thousand Parsec Server.

		(True, "Welcome to ABC") = connect("MyWonderfulClient")
		(False, "To busy atm!")  = connect("MyWonderfulClient")

		You can used the "failed" function to check the result.
		"""
		self._common()

		# Send a connect packet
		from version import version
		p = objects.Connect(self.no, ("libtpproto-py/%i.%i.%i " % version) + str)
		self._send(p)

		if self._noblock():
			self._append(self._connect, self.no)
			return None

		# and wait for a response
		return self._connect(self.no)

	def _connect(self, no):
		"""\
		*Internal*

		Completes the connect function, which will automatically change
		to an older version if server only supports it.
		"""
		p = self._recv([0, no])
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.OK):
			return True, p.s
		elif isinstance(p, objects.Fail):
			if p.protocol != objects.GetVersion():
				print "Changing version."
				if objects.SetVersion(p.protocol):
					return self.connect()
			return False, p.s
		elif isinstance(p, objects.Redirect):
			self.setup(p.s, nb=self._noblock(), debug=self.debug, proxy=self.proxy)
			return self.connect()
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def account(self, username, password, email, comment=""):
		"""\
		Tries to create an account on a Thousand Parsec Server.

		You can used the "failed" function to check the result.
		"""
		self._common()

		# Send a connect packet
		from version import version
		p = objects.Account(self.no, username, password, email, comment)
		self._send(p)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None

		# and wait for a response
		return self._okfail(self.no)

	def ping(self):
		"""\
		Pings the Thousand Parsec Server.

		(True, "Pong!") = ping()
		(False, "")     = ping()

		You can used the "failed" function to check the result.
		"""
		self._common()

		# Send a connect packet
		p = objects.Ping(self.no)
		self._send(p)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None

		# and wait for a response
		return self._okfail(self.no)

	def login(self, username, password):
		"""\
		Login to the server using this username/password.

		(True, "Welcome Mithro!")  = login("mithro", "mypassword")
		(False, "Go away looser!") = login("mithro", "mypassword")

		You can used the "failed" function to check the result.
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

	def features(self):
		"""\
		Gets the features the Thousand Parsec Server supports.

		FIXME: This documentation should be completed.
		"""
		self._common()

		# Send a connect packet
		p = objects.Feature_Get(self.no)
		self._send(p)

		if self._noblock():
			self._append(self._features, self.no)
			return None

		# and wait for a response
		return self._features(self.no)

	def _features(self, no):
		"""\
		*Internal*

		Completes the features function.
		"""
		p = self._recv(no)
		if not p:
			return None

		# Check it's the reply we are after
		if isinstance(p, objects.Feature):
			return p.features
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def time(self):
		"""\
		Gets the time till end of turn from a Thousand Parsec Server.

		FIXME: This documentation should be completed.
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
			# FIXME: This will cause any truth check to fail if p.time is zero!
			return p.time
		elif isinstance(p, objects.Fail):
			return False, p.s
		else:
			# We got a bad packet
			raise IOError("Bad Packet was received")

	def disconnect(self):
		"""\
		Disconnect from a server.

		This has no return. This function will either succeed or throw and exception.
		"""
		if self._noblock() and len(self.nb) > 0:
			raise IOError("Still waiting on non-blocking commands!")

		self.s.close()

	def get_object_ids(self, a=None, y=None, z=None, r=None, x=None, id=None, iter=False):
		"""\
		Get objects ids from the server,

		# Get all object ids (plus modification times)
		[(25, 10029436), ...] = get_object_ids()

		# Get all object ids (plus modification times) via an Iterator
		<Iter> = get_object_ids(iter=True)

		# Get all object ids (plus modification times) at a location
		[(25, 10029436), ..] = get_objects_ids(x, y, z, radius)
		[(25, 10029436), ..] = get_objects_ids(x=x, y=y, z=z, r=radius)

		# Get all object ids (plus modification times) at a location via an Iterator
		<Iter> = get_objects_ids(x, y, z, radius, iter=True)
		<Iter> = get_objects_ids(x=x, y=y, z=z, r=radius, iter=True)

		# Get all object ids (plus modification times) contain by an object
		[(25, 10029436), ..] = get_objects_ids(id)
		[(25, 10029436), ..] = get_objects_ids(id=id)

		# Get all object ids (plus modification times) contain by an object via an Iterator
		<Iter> = get_object_ids(id, iter=True)
		<Iter> = get_object_ids(id=id, iter=True)
		"""
		self._common()

		if a != None and y != None and z != None and r != None:
			x = a
		elif a != None:
			id = a

		p = None

		if x != None:
			p = objects.Object_GetID_ByPos(self.no, x, y, z, r)
		elif id != None:
			p = objects.Object_GetID_ByContainer(self.no, id)
		else:
			if iter:
				return self.IDIter(self, objects.Object_GetID)

			p = objects.Object_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_objects(self, a=None, id=None, ids=None, callback=None):
		"""\
		Get objects from the server,

		# Get the object with id=25
		[<obj id=25>] = get_objects(25)
		[<obj id=25>] = get_objects(id=25)
		[<obj id=25>] = get_objects(ids=[25])
		[<obj id=25>] = get_objects([id])

		# Get the objects with ids=25, 36
		[<obj id=25>, <obj id=36>] = get_objects([25, 36])
		[<obj id=25>, <obj id=36>] = get_objects(ids=[25, 36])
		"""
		self._common()

		if a != None:
			if hasattr(a, '__getitem__'):
				ids = a
			else:
				id = a

		if id != None:
			ids = [id]

		p = objects.Object_GetById(self.no, ids)
		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Object, self.no, callback)
			return None
		else:
			return self._get_header(objects.Object, self.no, callback)

	def get_orders(self, oid, *args, **kw):
		"""\
		Get orders from an object,

		# Get the order in slot 5 from object 2
		[<ord id=2 slot=5>] = get_orders(2, 5)
		[<ord id=2 slot=5>] = get_orders(2, slot=5)
		[<ord id=2 slot=5>] = get_orders(2, slots=[5])
		[<ord id=2 slot=5>] = get_orders(2, [5])

		# Get the orders in slots 5 and 10 from object 2
		[<ord id=2 slot=5>, <ord id=2 slot=10>] = get_orders(2, [5, 10])
		[<ord id=2 slot=5>, <ord id=2 slot=10>] = get_orders(2, slots=[5, 10])

		# Get all the orders from object 2
		[<ord id=2 slot=5>, ...] = get_orders(2)
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

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Order_Get(self.no, oid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Order, self.no, callback)
			return None
		else:
			return self._get_header(objects.Order, self.no, callback)

	def insert_order(self, oid, slot, otype, *args, **kw):
		"""\
		Add a new order to an object,

		(True, "Order inserted success")      = insert_order(oid, slot, otype, [arguments for order])
		(False, "Order couldn't be inserted") = insert_order(oid, slot, [Order Object])

		You can used the "failed" function to check the result.
		"""
		self._common()

		o = None
		if isinstance(otype, objects.Order) or isinstance(otype, objects.Order_Insert):
			o = otype
			o.no = objects.Order_Insert.no
			o._type = objects.Order_Insert.no

			o.id = oid
			o.slot = slot

			o.sequence = self.no
		else:
			o = apply(objects.Order_Insert, (self.no, oid, slot, otype,)+args, kw)

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
		[<Ok>] = remove_orders(2, 5)
		[<Ok>] = remove_orders(2, slot=5)
		[<Ok>] = remove_orders(2, slots=[5])
		[(False, "No order 5")] = remove_orders(2, [5])

		# Remove the orders in slots 5 and 10 from object 2
		[<Ok>, (False, "No order 10")] = remove_orders(2, [5, 10])
		[<Ok>, (False, "No order 10")] = remove_orders(2, slots=[5, 10])
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
			self._append(self._get_header, objects.OK, self.no)
			return None
		else:
			return self._get_header(objects.OK, self.no)

	def get_orderdesc_ids(self, iter=False):
		"""\
		Get orderdesc ids from the server,

		# Get all order description ids (plus modification times)
		[(25, 10029436), ...] = get_orderdesc_ids()

		# Get all order description ids (plus modification times) via an Iterator
		<Iter> = get_orderdesc_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.OrderDesc_GetID)

		p = objects.OrderDesc_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_orderdescs(self, *args, **kw):
		"""\
		Get order descriptions from the server. 

		Note: When the connection gets an order which hasn't yet been
		described it will automatically get an order description for that
		order, you don't need to do this manually.

		# Get the order description for id 5
		[<orddesc id=5>] = get_orderdescs(5)
		[<orddesc id=5>] = get_orderdescs(id=5)
		[<orddesc id=5>] = get_orderdescs(ids=[5])
		[(False, "No desc 5")] = get_orderdescs([5])

		# Get the order description for id 5 and 10
		[<orddesc id=5>, (False, "No desc 10")] = get_orderdescs([5, 10])
		[<orddesc id=5>, (False, "No desc 10")] = get_orderdescs(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.OrderDesc_Get(self.no, ids)
		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.OrderDesc, self.no, callback)
			return None
		else:
			return self._get_header(objects.OrderDesc, self.no, callback)

	def get_board_ids(self, iter=False):
		"""\
		Get board ids from the server,

		# Get all board ids (plus modification times)
		[(25, 10029436), ...] = get_board_ids()

		# Get all board ids (plus modification times) via an Iterator
		<Iter> = get_board_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Board_GetID)

		p = objects.Board_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_boards(self, x=None, id=None, ids=None, callback=None):
		"""\
		Get boards from the server,

		# Get the board with id=25
		[<board id=25>] = get_boards(25)
		[<board id=25>] = get_boards(id=25)
		[<board id=25>] = get_boards(ids=[25])
		[(False, "No such board")] = get_boards([id])

		# Get the boards with ids=25, 36
		[<board id=25>, (False, "No board")] = get_boards([25, 36])
		[<board id=25>, (False, "No board")] = get_boards(ids=[25, 36])
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
			self._append(self._get_header, objects.Board, self.no, callback)
			return None
		else:
			return self._get_header(objects.Board, self.no, callback)

	def get_messages(self, bid, *args, **kw):
		"""\
		Get messages from an board,

		# Get the message in slot 5 from board 2
		[<msg id=2 slot=5>] = get_messages(2, 5)
		[<msg id=2 slot=5>] = get_messages(2, slot=5)
		[<msg id=2 slot=5>] = get_messages(2, slots=[5])
		[(False, "No such 5")] = get_messages(2, [5])

		# Get the messages in slots 5 and 10 from board 2
		[<msg id=2 slot=5>, (False, "No such 10")] = get_messages(2, [5, 10])
		[<msg id=2 slot=5>, (False, "No such 10")] = get_messages(2, slots=[5, 10])
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

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Message_Get(self.no, bid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Message, self.no, callback)
			return None
		else:
			return self._get_header(objects.Message, self.no, callback)

	def insert_message(self, bid, slot, message, *args, **kw):
		"""\
		Add a new message to an board.

		Forms are
		[<Ok>] = insert_message(bid, slot, [arguments for message])
		[(False, "Insert failed")] = insert_message(bid, slot, [Message Object])
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
		[<Ok>] = remove_messages(2, 5)
		[<Ok>] = remove_messages(2, slot=5)
		[<Ok>] = remove_messages(2, slots=[5])
		[(False, "Insert failed")] = remove_messages(2, [5])

		# Remove the messages in slots 5 and 10 from board 2
		[<Ok>, (False, "No such 10")] = remove_messages(2, [10, 5])
		[<Ok>, (False, "No such 10")] = remove_messages(2, slots=[10, 5])
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

		p = objects.Message_Remove(self.no, oid, slots)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.OK, self.no)
			return None
		else:
			return self._get_header(objects.OK, self.no)

	def get_resource_ids(self, iter=False):
		"""\
		Get resource ids from the server,

		# Get all resource ids (plus modification times)
		[(25, 10029436), ...] = get_resource_ids()

		# Get all object ids (plus modification times) via an Iterator
		<Iter> = get_resource_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Resource_GetID)

		p = objects.Resource_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_resources(self, x=None, id=None, ids=None, callback=None):
		"""\
		Get resources from the server,

		# Get the resources with id=25
		[<board id=25>] = get_resources(25)
		[<board id=25>] = get_resources(id=25)
		[<board id=25>] = get_resources(ids=[25])
		[(False, "No such board")] = get_resources([id])

		# Get the resources with ids=25, 36
		[<board id=25>, (False, "No board")] = get_resources([25, 36])
		[<board id=25>, (False, "No board")] = get_resources(ids=[25, 36])
		"""
		self._common()

		# Setup arguments
		if id != None:
			ids = [id]
		if hasattr(x, '__getitem__'):
			ids = x
		elif x != None:
			ids = [x]

		p = objects.Resource_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Resource, self.no, callback)
			return None
		else:
			return self._get_header(objects.Resource, self.no, callback)

	def get_category_ids(self, iter=False):
		"""\
		Get category ids from the server,

		# Get all category ids (plus modification times)
		[(25, 10029436), ...] = get_category_ids()

		# Get all order category ids (plus modification times) via an Iterator
		<Iter> = get_category_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Category_GetID)

		p = objects.Category_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_categories(self, *args, **kw):
		"""\
		Get category information,

		# Get the information for category 5
		[<cat id=5>] = get_categories(5)
		[<cat id=5>] = get_categories(id=5)
		[<cat id=5>] = get_categories(ids=[5])
		[(False, "No such 5")] = get_categories([5])

		# Get the information for category 5 and 10
		[<cat id=5>, (False, "No such 10")] = get_categories([5, 10])
		[<cat id=5>, (False, "No such 10")] = get_categories(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Category_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Category, self.no, callback)
			return None
		else:
			return self._get_header(objects.Category, self.no, callback)

	def insert_category(self, *args, **kw):
		"""\
		Add a new category.

		<category> = insert_category(id, [arguments for category])
		<Fail> = insert_category([Category Object])
		"""
		self._common()

		d = None
		if isinstance(args[0], objects.Category) or isinstance(args[0], objects.Category_Add):
			d = args[0]
			d.no = objects.Category_Add.no
			d._type = objects.Category_Add.no

			d.sequence = self.no
		else:
			d = apply(objects.Category_Add, (self.no,)+args, kw)

		self._send(d)

		if self._noblock():
			self._append(self._get_single, objects.Category, self.no)
			return None
		else:
			return self._get_single(objects.Category, self.no)

	def remove_categories(self, a=None, id=None, ids=None):
		"""\
		Remove categories from the server,

		# Get the category with id=25
		[<ok>] = remove_categories(25)
		[<ok>] = remove_categories(id=25)
		[<ok>] = remove_categories(ids=[25])
		[<ok>] = remove_categories([id])

		# Get the categories with ids=25, 36
		[<ok>, <ok>] = remove_categories([25, 36])
		[<ok>, <ok>] = remove_categories(ids=[25, 36])
		"""
		self._common()

		if a != None:
			if hasattr(a, '__getitem__'):
				ids = a
			else:
				id = a

		if id != None:
			ids = [id]

		p = objects.Category_Remove(self.no, ids)
		self._send(p)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None
		else:
			return self._okfail(self.no)

	def get_design_ids(self, iter=False):
		"""\
		Get design ids from the server,

		# Get all design ids (plus modification times)
		[(25, 10029436), ...] = get_design_ids()

		# Get all order design ids (plus modification times) via an Iterator
		<Iter> = get_design_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Design_GetID)

		p = objects.Design_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_designs(self, *args, **kw):
		"""\
		Get designs descriptions,

		# Get the information for design 5
		[<des id=5>] = get_designs(5)
		[<des id=5>] = get_designs(id=5)
		[<des id=5>] = get_designs(ids=[5])
		[(False, "No such 5")] = get_designs([5])

		# Get the information for design 5 and 10
		[<des id=5>, (False, "No such 10")] = get_designs([5, 10])
		[<des id=5>, (False, "No such 10")] = get_designs(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Design_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Design, self.no, callback)
			return None
		else:
			return self._get_header(objects.Design, self.no, callback)

	def insert_design(self, *args, **kw):
		"""\
		Add a new design.

		<design> = insert_design(id, [arguments for design])
		<Fail> = insert_design([Design Object])
		"""
		self._common()

		d = None
		if isinstance(args[0], objects.Design) or isinstance(args[0], objects.Design_Add):
			d = args[0]
			d.no = objects.Design_Add.no
			d._type = objects.Design_Add.no

			d.sequence = self.no
		else:
			d = apply(objects.Design_Add, (self.no,)+args, kw)

		self._send(d)

		if self._noblock():
			self._append(self._get_single, objects.Design, self.no)
			return None
		else:
			return self._get_single(objects.Design, self.no)

	def change_design(self, *args, **kw):
		"""\
		Change a new design.

		<design> = change_design(id, [arguments for design])
		<Fail> = change_design([Design Object])
		"""
		self._common()

		d = None
		if isinstance(args[0], objects.Design) or isinstance(args[0], objects.Design_Add):
			d = args[0]
			d.no = objects.Design_Add.no
			d._type = objects.Design_Add.no

			d.sequence = self.no
		else:
			d = apply(objects.Design_Add, (self.no,)+args, kw)

		self._send(d)

		if self._noblock():
			self._append(self._get_single, objects.Design, self.no)
			return None
		else:
			return self._get_single(objects.Design, self.no)

	def remove_designs(self, a=None, id=None, ids=None):
		"""\
		Remove designs from the server,

		# Get the design with id=25
		[<ok>] = remove_designs(25)
		[<ok>] = remove_designs(id=25)
		[<ok>] = remove_designs(ids=[25])
		[<ok>] = remove_designs([id])

		# Get the designs with ids=25, 36
		[<ok>, <ok>] = remove_designs([25, 36])
		[<ok>, <ok>] = remove_designs(ids=[25, 36])
		"""
		self._common()

		if a != None:
			if hasattr(a, '__getitem__'):
				ids = a
			else:
				id = a

		if id != None:
			ids = [id]

		p = objects.Design_Remove(self.no, ids)
		self._send(p)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None
		else:
			return self._okfail(self.no)

	def get_component_ids(self, iter=False):
		"""\
		Get component ids from the server,

		# Get all component ids (plus modification times)
		[(25, 10029436), ...] = get_component_ids()

		# Get all order component ids (plus modification times) via an Iterator
		<Iter> = get_component_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Component_GetID)

		p = objects.Component_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_components(self, *args, **kw):
		"""\
		Get components descriptions,

		# Get the description for components 5
		[<com id=5>] = get_components(5)
		[<com id=5>] = get_components(id=5)
		[<com id=5>] = get_components(ids=[5])
		[(False, "No such 5")] = get_components([5])

		# Get the descriptions for components 5 and 10
		[<com id=5>, (False, "No such 10")] = get_components([5, 10])
		[<com id=5>, (False, "No such 10")] = get_components(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Component_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Component, self.no, callback)
			return None
		else:
			return self._get_header(objects.Component, self.no, callback)

	def get_property_ids(self, iter=False):
		"""\
		Get property ids from the server,

		# Get all property ids (plus modification times)
		[(25, 10029436), ...] = get_property_ids()

		# Get all order property ids (plus modification times) via an Iterator
		<Iter> = get_property_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.Property_GetID)

		p = objects.Property_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_properties(self, *args, **kw):
		"""\
		Get properties descriptions,

		# Get the description for properties 5
		[<pro id=5>] = get_properties(5)
		[<pro id=5>] = get_properties(id=5)
		[<pro id=5>] = get_properties(ids=[5])
		[(False, "No such 5")] = get_properties([5])

		# Get the descriptions for properties 5 and 10
		[<pro id=5>, (False, "No such 10")] = get_properties([5, 10])
		[<pro id=5>, (False, "No such 10")] = get_properties(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Property_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Property, self.no, callback)
			return None
		else:
			return self._get_header(objects.Property, self.no, callback)

	def get_players(self, *args, **kw):
		"""\
		Get players descriptions,

		# Get the description for players 5
		[<pro id=5>] = get_players(5)
		[<pro id=5>] = get_players(id=5)
		[<pro id=5>] = get_players(ids=[5])
		[(False, "No such 5")] = get_players([5])

		# Get the descriptions for players 5 and 10
		[<pro id=5>, (False, "No such 10")] = get_players([5, 10])
		[<pro id=5>, (False, "No such 10")] = get_players(ids=[5, 10])
		"""
		self._common()

		if kw.has_key('ids'):
			ids = kw['ids']
		elif kw.has_key('id'):
			ids = [kw['id']]
		elif len(args) == 1 and hasattr(args[0], '__getitem__'):
			ids = args[0]
		else:
			ids = args

		if kw.has_key('callback'):
			callback = kw['callback']
		else:
			callback = None

		p = objects.Player_Get(self.no, ids)

		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.Player, self.no, callback)
			return None
		else:
			return self._get_header(objects.Player, self.no, callback)

