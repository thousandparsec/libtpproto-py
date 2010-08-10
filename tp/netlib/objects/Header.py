
from xstruct import pack, unpack, hexbyte

# Squash warnings about hex/oct
import warnings

_marker = []

class FrameError(Exception):
	pass

class Header(object):
	"""\
	Base class for all packets.

	Includes all the common parts for the packets.

	The class can be instansated however it will morph into
	into the correct packet type once the process function
	is called with data.

	Example:

		p = Header.new(data)
		str(p)
		'<Object instance at 0x401ee50c>'
	"""

	size=4+4+4+4
	struct="2sBBIII"


	class VersionError(Exception):
		pass

	def __init__(self, protocol, majorv, minorv, sequence, type, length):
		"""\
		Create a new header object.

		It takes a string which contains the "header" data.
		"""
		self.protocol = protocol
		self.majorv   = majorv
		self.minorv   = minorv
		self.sequence = sequence
		self._type    = type
		self._length  = length

		# Upgrade the class to the real type
		if self.__class__ == Header:
			try:
				self.__class__ = self.mapping[type]
			except KeyError, e:
				raise ValueError("Unknown packet type %i." % type)

	def __eq__(self, other):
		if type(self) == type(other):
			for key in self.__dict__.keys():
				if key.startswith('_'):
					continue

				if getattr(other, key, None) != self.__dict__[key]:
					return False
			return True
		return False

	def __repr__(self):
		"""\
		Return a reconisable string.
		"""
		return "<%s - %s @ %s (seq: %i)>" % \
			(self.__class__.__module__, self.__class__.__name__, hex(id(self)),
				self.sequence)

	def pack(self):
		"""\
		Produce a string suitable to be send over the wire.
		"""
		return pack(Header.struct, self.protocol, self.majorv, self.minorv, self.sequence, self._type, 0)

	def __str__(self):
		output = self.pack()
		length = len(output) - Header.size
		return output[:Header.size-4] + pack(Header.struct[-1], length) + output[Header.size:]

	def fromstr(cls, data):
		"""\
		Look at the packet type and morph this object into the
		correct type.
		"""
		args, extra = unpack(Header.struct, data)
		if len(extra) > 0:
			raise ValueError('Got too much data! %s bytes remaining' % len(extra))

		return cls(*args)
	fromstr = classmethod(fromstr)

	def data_set(self, data=None):
		"""\
		Processes the data of the packet.
		"""
		if self.data == None:
			self._length = 0
		else:
			self._length = len(data)


class Processed(Header):
	"""\
	Base class for packets.
	"""
	struct_callback = None

	def __init__(self, sequence):
		Header.__init__(self, "TP", 4, 0, sequence, self.no, -1)
		
	def __process__(self, data):
		try:
			args, leftover = unpack(self.struct, data, callback=self.struct_callback)
		except TypeError, e:
			raise TypeError("Problem when trying to unpack %s (%s) %s" % (self.__class__, self.struct, e))

		if len(leftover) > 0:
			raise ValueError("Left over data found for %r: '%r'" % (self.__class__.__name__, leftover))

		self.__init__(self.sequence, *args)

