
from xstruct import pack, unpack, hexbyte

version = "TP02"

_marker = []

class FrameError(Exception):
	pass

class Header:
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

	def __init__(self, s):
		"""\
		Create a new header object.

		It takes a string which contains the "header" data.
		"""
		self.process = self.__process__
		
		output, extra = unpack(Header.struct, s)
		self.protocol, self.sequence, self._type, self.length = output

		# Sanity Checks
		if self.protocol != version:
			raise ValueError("Invalid creation string\n%s\n" % hexbyte(s))
			
		if len(extra) == self.length:
			self.process(extra)
		elif len(extra) != 0:
			raise ValueError("Invalid input string")

	def __getattr__(self, key, default=_marker):
		hk = self.__dict__.has_key
		d = self.__dict__
	
		# Don't allow any access to anything apart from process 
		# (except in the case of zero length)
		if hk("process"):
			if key == "process" or key == "length" or key[0:2] == "__":
				try:
					return d[key]
				except:
					try:
						return getattr(self.__class__, key)
					except AttributeError, e:
						if default == _marker:
							raise AttributeError("No such attribute '%s'" % key)
						else:
							return default
			else:
				raise AttributeError("Cannot do anything till you call process!")
		else:
			try:
				return d[key]
			except:
				try:
					return getattr(self.__class__, key)
				except AttributeError, e:
					if default == _marker:
						raise AttributeError("No such attribute '%s'" % key)
					else:
						return default

	def __str__(self):
		"""\
		Return a reconisable string.
		"""
		return "<%s @ %s>" % (self.__class__, hex(id(self)))

	def __repr__(self):
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
		
		# Remove the process function
		del self.__dict__["process"]
		
		# Mutate this class
		self.__class__ = Header.mapping[self._type]

		# Do the class specific function
		apply(self.__init__, \
			(self.sequence,) + unpack(self.struct, data)[0])

		
	def set_data(self, data=None):
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
		
		self.protocol = version

		self._type = self.no
		self.sequence = sequence
	
