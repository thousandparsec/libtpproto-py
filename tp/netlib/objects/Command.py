
from xstruct import pack, unpack

from Description import Describable, DescriptionError
from CommandDesc import descriptions

class Command(Describable):
	"""\
 	A Command packet.
	The Command packet consists of:
		* a UInt32, Command type ID
		* extra data, as defined by each command type
	"""
	no = 1006
	struct = "I"

	_name = "Unknown Command"

	def __init__(self, sequence, \
			id,	subtype, *args, **kw):
		Describable.__init__(self, sequence)

		self.length = \
			4 + 4 + 4 + 4 + \
			4 + len(resources)*(4+4)

		self.id        = id
		self._subtype  = subtype

		if self.__class__ == Command:
			try:
				if kw.has_key('force'):
					cls = kw['force']
					del kw['force']
				else:
					cls = descriptions()[subtype]

				self.__class__ = cls
				if len(args) > 0:
					self.__init__(sequence, id,	subtype, *args, **kw)
			except KeyError, e:
				raise DescriptionError(sequence, subtype)

	def __str__(self):
		output = Describable.__str__(self)
		output += pack(self.struct, self.id, self._subtype)
		return output

	def __repr__(self):
		"""\
		Return a reconisable string.
		"""
		return "<Command - %s @ %s (seq: %i length: %i)>" % \
			(self.__class__.__name__, hex(id(self)), self.sequence, self.length)

