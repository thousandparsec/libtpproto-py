
from xstruct import pack

from Description import Description
from constants import *

# Import prebuild orders
from ObjectDesc import splitall, edir, import_subtype, ClassNicePrint
_descriptions = None
def descriptions(added=None):
	global _descriptions

	if _descriptions == None:
		try:
			_descriptions = import_subtype(edir(__file__), py2exe=__loader__)
		except NameError, e:
			try:
				import sys
				if sys.frozen == "macosx_app":
					raise AttributeError("macosx_app")
				print sys.frozen
				import carchive
				this = carchive.CArchive(sys.executable).openEmbeddedZlib("out1.pyz")
				_descriptions = import_subtype("tp.netlib.objects.OrderExtra", installer=this.contents())
			except AttributeError, e:
				_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
	
	return _descriptions


from Header import Header
from Order import Order

from tp.netlib.objects.parameters import OrderParamsMapping
class DynamicBaseOrder(Order):
	"""\
	An Order Type built by a OrderDesc.
	"""
	substruct = ""
	subtype = -1
	name = "Base"

	__metaclass__ = ClassNicePrint

	def __init__(self, sequence, id, slot, subtype, turns, resources, *args, **kw):
		Order.__init__(self, sequence, id, slot, subtype, turns, resources)

		assert subtype == self.subtype, "Type %s does not match this class %s" % (subtype, self.__class__)

		if len(self.properties) != len(args):
			raise TypeError("The args where not correct, they should be of length %s" % len(self.properties))

		for property, arg in zip(self.properties, args):
			setattr(self, property.name, arg)

	def pack(self):
		output = [Order.pack(self)]
		for property in self.properties:
			arg = list(getattr(self, property.name))
			output.append(property.pack(arg))
			
		return "".join(output)

	def __repr__(self):
		return "<netlib.objects.OrderExtra.DynamicOrder - %s @ %s>" % (self._name, hex(id(self)))

	def __process__(self, leftover, **kw):
		moreargs = []

		# Unpack the described data
		for property in self.properties:
			args, leftover = property.unpack(leftover)
			moreargs.append(args)

		if len(leftover) > 0:
			raise ValueError("\nError when processing %s.\nExtra data found: %r " % (self.__class__, leftover))

		args = [self.id, self.slot, self.subtype, self.turns, self.resources]
		self.__init__(self.sequence, *(args + moreargs))

class OrderDesc(Description):
	"""\
	The OrderDesc packet consists of:
		* a UInt32, order type
		* a String, name
		* a String, description
		* a list of
			* a String, argument name
			* a UInt32, argument type
			* a String, description
		* a UInt64, the last time the description was modified
	"""
	no = 9
	struct="I SS [SIS] T"


	def __init__(self, sequence, \
			id, name, description, \
			arguments, modify_time):
		Description.__init__(self, sequence, id)

		self._name = name
		self.description = description
		self.arguments = arguments
		self.modify_time = modify_time

	def pack(self):
		output = Description.pack(self)
		output += pack(self.struct, \
				self.id, \
				self._name, \
				self.description, \
				self.arguments, \
				self.modify_time)

		return output

	def build(self):
		"""\
		*Internal*

		Builds a class from this description.
		"""
		class DynamicOrder(DynamicBaseOrder):
			pass

		DynamicOrder._name = self._name
		DynamicOrder.doc = self.description

		# Arguments
		DynamicOrder.subtype = self.id
		DynamicOrder.substruct = ""

		DynamicOrder.properties = []
		for name, type, desc in self.arguments:

			property = OrderParamsMapping[type](name=name, desc=desc)

			DynamicOrder.properties.append(property)
			setattr(DynamicOrder, name, property)

		DynamicOrder.modify_time = self.modify_time
		DynamicOrder.packet = self

		return DynamicOrder

	def register(self):
		descriptions(self.build())

__all__ = ["descriptions", "OrderDesc"]
