"""\
This module contains the administration client connections.
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

from client import failed

sequence_max = 4294967296

class AdminClientConnection(Connection):
	"""\
	Class for an administration connection from the client side.
	"""

	def __init__(self, host=None, port=None, nb=0, debug=False):
		Connection.__init__(self)

		self.buffered['undescribed'] = {}
		self.buffered['store'] = {}

		if host != None:
			self.setup(host, port, nb, debug)

		self.__desc = False

	def setup(self, host, port=None, nb=0, debug=False, proxy=None):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		hoststring = host
		self.proxy = None
		
		if hoststring.startswith("tp://") or hoststring.startswith("tps://"):
			if hoststring.startswith("tp://"):
				host = hoststring[5:]
				if not port:
					port = 6925
			elif hoststring.startswith("tps://"):
				host = hoststring[6:]
				if not port:
					port = 6926

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
					port = 6925

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
			print "Creating SSL wrapper...."
			s = SSLWrapper(s)

		self.hoststring = hoststring
		self.host = host
		self.port = port

		Connection.setup(self, s, nb=nb, debug=debug)
		self.no = 1

	def _description_error(self, p):
		# Need to figure out how to do non-blocking properly...
		#Send a request for the description
		if not self.__desc:
			q = objects.OrderDesc_Get(p.sequence-1, [p._subtype])
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
					raise IOError("Failed to get remaining IDs (%s)" % (p[1]))

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
		p = objects.Connect(self.no, ("libtpproto-py/%i.%i.%i " % version[:3]) + str)
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

	def disconnect(self):
		"""\
		Disconnect from a server.

		This has no return. This function will either succeed or throw and exception.
		"""
		if self._noblock() and len(self.nb) > 0:
			raise IOError("Still waiting on non-blocking commands!")

		self.s.close()

    #TODO: this is incomplete pending objects.Command design
	def send_command(self, ctype, *args, **kw):
		"""\
		Send a command to the server.
		"""
		self._common()

		c = None
		if isinstance(ctype, objects.Command):
			c = ctype
			c.no = objects.Command.no
			c._type = objects.Command.no

			c.sequence = self.no
		else:
			c = objects.Command(self.no, ctype, 0, [], *args)

		self._send(c)

		if self._noblock():
			self._append(self._okfail, self.no)
			return None

		# and wait for a response
		return self._okfail(self.no)

	def get_commanddesc_ids(self, iter=False):
		"""\
		Get commanddesc ids from the server,

		# Get all command description ids (plus modification times)
		[(25, 10029436), ...] = get_commanddesc_ids()

		# Get all command description ids (plus modification times) via an Iterator
		<Iter> = get_commanddesc_ids(iter=True)
		"""
		self._common()

		if iter:
			return self.IDIter(self, objects.CommandDesc_GetID)

		p = objects.CommandDesc_GetID(self.no, -1, 0, -1)

		self._send(p)
		if self._noblock():
			self._append(self._get_idsequence, self.no, iter)
			return None
		else:
			return self._get_idsequence(self.no, iter)

	def get_commanddescs(self, *args, **kw):
		"""\
		Get command descriptions from the server. 

		Note: When the connection gets a command which hasn't yet been
		described it will automatically get a command description for that
		command, you don't need to do this manually.

		# Get the command description for id 5
		[<cmddesc id=5>] = get_commanddescs(5)
		[<cmddesc id=5>] = get_commanddescs(id=5)
		[<cmddesc id=5>] = get_commanddescs(ids=[5])
		[(False, "No desc 5")] = get_commanddescs([5])

		# Get the command description for id 5 and 10
		[<cmddesc id=5>, (False, "No desc 10")] = get_commanddescs([5, 10])
		[<cmddesc id=5>, (False, "No desc 10")] = get_commanddescs(ids=[5, 10])
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

		p = objects.CommandDesc_Get(self.no, ids)
		self._send(p)

		if self._noblock():
			self._append(self._get_header, objects.CommandDesc, self.no, callback)
			return None
		else:
			return self._get_header(objects.CommandDesc, self.no, callback)
