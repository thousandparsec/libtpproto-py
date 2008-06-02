
from xstruct import pack, unpack

from Description import Describable

class Object(Describable):
	"""\
	The Object packet consists of:
		* a UInt32, object ID
		* a UInt32, object type
		* a String, name of object
		* a String, description of the object
		* a UInt32, parent ID
		* a list of UInt32, object IDs of objects contained in the current object
		* a UInt64, the last modified time
		* 16 bytes of padding, for future expansion of common attributes
		* extra data, as defined by each object type
	"""
	no = 7
	struct = "IISS I [I] T 16x"

	_name = "Unknown Object"

	def __init__(self, sequence, \
			id, subtype, name, \
			desc, \
			parent, \
			contains, \
			modify_time, \
			*args, **kw):
		Describable.__init__(self, sequence)

		self.length = \
			4 + 4 + \
			4 + len(name) + \
			4 + len(desc) + \
			4 + \
			4 + len(contains)*4 + \
			8 + 16

		self.id           = id
		self._subtype     = subtype
		self.name         = name
		self.desc         = desc
		self.parent       = parent
		self.contains     = contains
		self.modify_time  = modify_time

		if self.__class__ == Object:
			try:
				if kw.has_key('force'):
					cls = kw['force']
					del kw['force']
				else:
					from ObjectDesc import descriptions
					cls = descriptions()[subtype]

				self.__class__ = cls
				if len(args) > 0:
					self.__init__(sequence, \
									id, subtype, name, \
									desc, \
									parent, \
									contains, \
									modify_time, \
									*args)

			except KeyError, e:
				raise DescriptionError(sequence, subtype)

	def __str__(self):
		output = Describable.__str__(self)
		output += pack(self.struct, \
				self.id, \
				self._subtype, \
				self.name, \
				self.desc, \
				self.parent, \
				self.contains, \
				self.modify_time)
		return output

	def __repr__(self):
		"""\
		Return a reconisable string.
		"""
		return "<%s @ %s>" % \
			(self.__class__.__name__, self.id)
		return "<%s @ %s (seq: %i length: %i)>" % \
			(self.__class__.__name__, hex(id(self)),
				self.sequence, self.length)
