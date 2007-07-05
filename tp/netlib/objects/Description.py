
from xstruct import pack, unpack
from Header import Processed

class DescriptionError(Exception):
	"""\
	Thrown by objects which can't find the description which describes
	them.
	"""
	pass

class Describable(Processed):
	"""\
	The Describable packet uses other packets to describe "extra" details
	about the packet.
	"""
	substruct = ""

	def __process__(self, data, **kw):
		# Unpack the first lot of data
		args, leftover = unpack(self.struct, data)
		self.__init__(self.sequence, *args, **kw)

		# Unpack the second lot of data
		try:
			moreargs, leftover2 = unpack(self.substruct, leftover)
			if len(leftover2) > 0:
				raise ValueError("\nError when processing %s.\nExtra data found: %r \nStructure: %s, Data: %r" % (self.__class__, leftover2, self.substruct, leftover))
		except TypeError, e:
			raise ValueError("\nError when processing %s.\nNot enough data found: %s\nStructure: %s, Data: %r" % (self.__class__, e, self.substruct, leftover))

		self.__init__(self.sequence, *(args + moreargs))

class Description(Processed):
	"""\
	The Description packet contains the description of another type of
	packet.

	The id is equal to the subtype.
	"""
	def __init__(self, sequence, id):
		Processed.__init__(self, sequence)
		self.id = id


