
from xstruct import pack, unpack, hexbyte

# Squash warnings about hex/oct
import warnings

versions = ["TP03"]
version = "TP03"

def SetVersion(i):
	global version

	if i in versions:
		version = i
		return True
	else:
		return False
		
def GetVersion():
	global version
	return version

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

		p = Header(data)
		str(p)
		'<Object instance at 0x401ee50c>'
	"""

	size=4+4+4+4
	struct="4sIII"

	class VersionError(Exception):
		pass

	def __init__(self, protocol, sequence, type, length):
		"""\
		Create a new header object.

		It takes a string which contains the "header" data.
		"""
		self.protocol = protocol
		self.sequence = sequence
		self._type    = type
		self.length   = length

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
		return "<%s - %s @ %s (seq: %i length: %i)>" % \
			(self.__class__.__module__, self.__class__.__name__, hex(id(self)),
				self.sequence, self.length)

	def __str__(self):
		"""\
		Produce a string suitable to be send over the wire.
		"""
		output = pack(Header.struct, self.protocol, self.sequence, self._type, self.length)
		return output

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
			self.length = 0
		else:
			self.length = len(data)


class Processed(Header):
	"""\
	Base class for packets.
	"""

	def __init__(self, sequence):
		Header.__init__(self, version, sequence, self.no, -1)
		
	def __process__(self, data):
		args, leftover = unpack(self.struct, data)
		if len(leftover) > 0:
			raise ValueError("Left over data found for %r: '%r'" % (self.__class__.__name__, leftover))

		self.__init__(self.sequence, *args)

