
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

	def __init__(self, s, protocol=None):
		"""\
		Create a new header object.

		It takes a string which contains the "header" data.
		"""
		self.process = self.__process__
	
		if protocol == None:
			protocol = version
	
		output, extra = unpack(Header.struct, s)
		self.protocol, self.sequence, self._type, self.length = output

		# Sanity Checks
		if self.protocol != protocol:
			if self.protocol[:2] == "TP":
				raise self.VersionError("Wrong version %s\n" % self.protocol)
			else:
				raise ValueError("Invalid creation string\n%s\n" % hexbyte(s))

		if self.length != 0 and len(extra) == self.length:
			self.process(extra)
		elif len(extra) != 0:
			raise ValueError("Invalid input string")

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

	def __process__(self, data):
		"""\
		Look at the packet type and morph this object into the
		correct type.
		"""
		# Make sure the data is correct length
		if len(data) != self.length:
			raise ValueError("Data not the correct length, Required: %s Got: %s" % \
				(self.length, len(data)) )
		
		# Mutate this class
		self.__class__ = Header.mapping[self._type]
		args, extra = unpack(self.struct, data)

		# Do the class specific function
		if hasattr(self, "process_extra"):
			apply(self.__init__, (self.sequence,) + args, {'extra':extra})
		else:
			apply(self.__init__, (self.sequence,) + args)

			if len(extra) != 0:
				raise ValueError("Extra Data found;" + extra)
		self.process = None

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
		
		if not hasattr(self, "protocol"):
			self.protocol = version
		
		self._type = self.no
		self.sequence = sequence
