
# Python imports
import socket

# Local imports
import xstruct
import objects

from support.output import *

_continue = []

class Connection:
	"""\
	Base class for Thousand Parsec protocol connections.
	Methods common to both server and client connections
	go here.
	"""

	def __init__(self):
		self.buffers = {}
		# This is a storage for out of sequence packets
		self.buffers['receive'] = {}

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
			green("Sending: %s (%s)\n" % (str(p), p.sequence))
			green("Sending: %s \n" % xstruct.hexbyte(repr(p)))
		s(repr(p))

	def _recv(self, sequence):
		"""\
		*Internal*
		
		Reads a single TP packet with correct sequence number from the socket.
		"""
		# FIXME: Need to make this more robust for bad packets
		r = self.s.recv
		b = self.buffers['receive']
		s = objects.Header.size
		
		p = None
		
		# Check we don't already have a packet
		if b.has_key(sequence) and len(b[sequence]) > 0:
			p = b[sequence].pop(0)

		while p == None:
			# Is a packet header on the line?
			try:
				h = r(s, socket.MSG_PEEK)
			
				if len(h) == 0:
					raise IOError("Socket has been terminated.")
			except socket.error, e:
				h = ""

			# This will only ever occur on a non-blocking connection
			if len(h) != s:
				return None
			
			if self.debug:
				red("Receiving: %s" % xstruct.hexbyte(h))
			
			p = objects.Header(h)
				
			if p.length > 0:
				d = r(s+p.length, socket.MSG_PEEK)
				
				if self.debug:
					red("%s \n" % xstruct.hexbyte(d[s:]))
			
				# This will only ever occur on a non-blocking connection
				if len(d) != s+p.length:
					return None
			
			else:
				d = ""
			
			# Remove the stuff from the line
			r(s+p.length)

			try:
				p.process(d[s:])
			except objects.DescriptionError:
				p._data = d[s:]
				p = self._description_error(p)
				continue

			if self.debug:
				red("Receiving: %s (%s)\n" % (str(p), p.sequence))

			# FIXME: This shouldn't be in the base class
			# Check if this packet is a description for an undescribed object
			if isinstance(p, objects.Description):
				p = self._description(p)
				
			# Check its the type of packet we are after
			if p.sequence != sequence:
				if not b.has_key(sequence):
					b[p.sequence] = []
					
				b[p.sequence].append(p)

				p = None
				continue

		return p

	def _description_error(self, packet):
		"""\
		Called when we get a packet which hasn't be described.

		The packet will be of type Header ready to be morphed by calling
		process as follows,
		
		p.process(p._data)
		"""
		raise objects.DescriptionError("Can not deal with an undescribed packet.")

	def _description(self, packet):
		"""\
		Called when we get a description error.
		"""
		return packet

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

