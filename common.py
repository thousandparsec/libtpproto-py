
# Python imports
import socket

# Local imports
import xstruct
import objects

from support.output import *

_continue = []

class l(list):
	def __str__(self):
		return "[%s]" % ", ".join([str(i) for i in self])

class NotImplimented(Exception):
	pass

class SSLWrapper:
	def __init__(self, s):
		self.s = socket.ssl(s)

	def send(self, data):
		no = 0
		while no != len(data):
			no += self.s.write(data)
	
	def recv(self, amount):
		return self.s.read(amount)

class Connection:
	"""\
	Base class for Thousand Parsec protocol connections.
	Methods common to both server and client connections
	go here.
	"""

	def __init__(self):
		self.buffer = ""
		self.buffered = {}
		# This is a storage for out of sequence packets
		self.buffered['receive'] = {}

	def setup(self, s, nb=False, debug=False):
		"""\
		*Internal*

		Sets up the socket for a connection.
		"""
		self.s = s
	
		self.setblocking(nb)
		self.debug = debug

	def setblocking(self, nb):
		"""\
		Sets the connection to either blocking or non-blocking.
		"""
		if not nb and self._noblock():
			# Check we arn't waiting on anything
			if len(self.nb) > 0:
				raise IOError("Still waiting on non-blocking commands!")
				
			self.s.setblocking(1)
			del self.nb

		elif nb and not self._noblock():
			self.s.setblocking(0)
			self.nb = []

	def pump(self):
		"""\
		Causes the connection to read and process stuff from the
		buffer. This will allow you to read out of band messages.

		Calling oob will also cause the connection to be pumped.
		"""
		noblock = self._noblock()
		if not noblock:
			self.setblocking(1)
		
		self._recv(-1)
		
		if not noblock:
			self.setblocking(0)

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
		if self.debug:
			green("Sending: %s (%s)\n" % (repr(p), p.sequence))
			green("Sending: %s \n" % xstruct.hexbyte(str(p)))
		s(str(p))

	def _recv(self, sequence):
		"""\
		*Internal*
		
		Reads a single TP packet with correct sequence number from the socket.
		"""
		if not hasattr(sequence, '__getitem__'):
			sequences = [sequence]
		else:
			sequences = sequence
		
		# FIXME: Need to make this more robust for bad packets
		r = self.s.recv
		buffered = self.buffered['receive']
		size = objects.Header.size
		p = None

		while p == None:
			for sequence in sequences:
				if buffered.has_key(sequence) and len(buffered[sequence]) > 0:
					break
			
			if buffered.has_key(sequence) and len(buffered[sequence]) > 0:
				p = buffered[sequence][0]
			
				try:
					p.process(p._data)
					del buffered[sequence][0]
					
				except objects.DescriptionError:
					self._description_error(p)
					p = None
				except Exception, e:
					self._error(p)
					p = None
					del buffered[sequence][0]

				for k in buffered.keys():
					if len(buffered[k]) == 0:
						del buffered[k]
				continue
				
			# Get the data on the line
			data = r(size-len(self.buffer))
			if data is None:
				data = ""
			elif len(data) == 0:
				raise IOError("Socket has been terminated.")
			self.buffer += data

			# This will only ever occur on a non-blocking connection
			if len(self.buffer) < size:
				if self._noblock():
					return None
				else:
					print "Ekk! Not enough data on a blocking connection..."
					continue

			h = self.buffer[:size]
			if self.debug:
				red("Receiving: %s" % xstruct.hexbyte(h))
			
			q = objects.Header(h)	
			if q.length > 1024*1024:
				raise IOError("Packet was to large!")
			
			if len(self.buffer) < size+q.length:
				self.buffer += r(size+q.length-len(self.buffer))

			# This will only ever occur on a non-blocking connection
			if len(self.buffer) < size+q.length:
				if self._noblock():
					return None
				else:
					print "Ekk! Not enough data on a blocking connection..."
					continue
				
			if self.debug:
				red("%s \n" % xstruct.hexbyte(self.buffer[size:size+q.length]))
			
			q._data, self.buffer = self.buffer[size:size+q.length], self.buffer[size+q.length:]
			
			if not buffered.has_key(q.sequence):
				buffered[q.sequence] = []	
			buffered[q.sequence].append(q)

		if self.debug:
			red("Receiving: %s (%s)\n" % (repr(p), p.sequence))

		return p

	def _description_error(self, packet):
		"""\
		Called when we get a packet which hasn't be described.

		The packet will be of type Header ready to be morphed by calling
		process as follows,
		
		p.process(p._data)
		"""
		raise objects.DescriptionError("Can not deal with an undescribed packet.")

	def _version_error(self, h):
		"""\
		Called when a packet of the wrong version is found.

		The function should either raise the error or return a
		packet with the correct version.
		"""
		print "Version Error"
		return objects.Header(h, h[:4])

	def _error(self, packet):
		raise

	############################################
	# Non-blocking helpers
	############################################
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

	def _insert(self, function, *args):
		"""\
		*Internal*

		Queues a fuction for polling before the current one.
		"""
		self.nb.insert(0, (function, args))

	def _next(self, function, *args):
		"""\
		*Internal*

		Queues a fuction for polling after the current one.
		"""
		self.nb.insert(1, (function, args))
		
	def _append(self, function, *args):
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

