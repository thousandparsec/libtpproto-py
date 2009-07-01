
import sys
import site
import string
import os
from os import path

from xstruct import pack, unpack

def splitall(p, extra = []):
	bits = []
	while not p in ['', '..', '.'] \
		and not p in getattr(site, 'sitedirs', ()) \
		and not p in sys.path \
		and not p in extra:
		p, c = os.path.split(p)
		bits.append(c)
	bits.reverse()
	return bits	

def edir(p):
	extra = path.splitext(path.basename(p))[0][:-4] + "Extra"
	d = path.join(path.dirname(p), extra)

	return d

def import_subtype(p, py2exe=None, installer=None):
	subtypes = {}

	if py2exe != None:
		paths = splitall(p, py2exe.archive)
	elif installer != None:
		paths = p.split(".")
	else:
		paths = splitall(p)
	import_base = string.join(paths, ".")

	if py2exe != None:
		files = []
		for thing in py2exe._files.values():
			file = thing[0]
			if p in file:
				files.append(file)
	elif installer != None:
		files = []
		for file in installer:
			if file.startswith(import_base + "."):
				files.append(file[len(import_base)+1:] + ".py")
	else:
		files = os.listdir(p)

	for file in files:
		name, ext = path.splitext(path.basename(file))
		if not ext in [".py", ".pyc", ".pyo"] or name == "__init__":
			continue
			
		try:
			s = "from %s import %s\nlib = %s" % (import_base, name, name)
			exec(s)
#			lib = __import__("%s.%s" % (import_base, name), globals(), locals(), [name])
		except ImportError, e:
			print "Import Error", e

		if not hasattr(lib, name):
			continue
		
		cl = getattr(lib, name)
		if not hasattr(cl, "subtype"):
			continue
			
		if subtypes.has_key(cl.subtype):
			continue
		
		subtypes[cl.subtype] = cl

	return subtypes

from Description import Description
from constants import *

# Import prebuild orders
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
				_descriptions = import_subtype("tp.netlib.objects.ObjectExtra", installer=this.contents())
			except AttributeError, e:
				_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
	
	return _descriptions

class ClassNicePrint(type):
	def __str__(self):
		return "<dynamic-class '%s' (%s) at %s>" % (self._name, self.subtype, hex(id(self)))
	__repr__ = __str__

from Header import Header
from Object import Object

from tp.netlib.objects.parameters import ObjectParamsMapping, ObjectParamsStructDesc, GroupStructure
class DynamicBaseObject(Object):
	"""\
	An Object Type built by a ObjectDesc.
	"""
	substruct = ""
	subtype = -1
	name = "Base"

	__metaclass__ = ClassNicePrint

	def __init__(self, sequence, \
			id, subtype, name, \
			desc, \
			parent, \
			contains, \
			modify_time, \
			*args, **kw):
		Object.__init__(self, sequence, id, subtype, name, desc, parent, contains, modify_time)

		assert subtype == self.subtype, "Type %s does not match this class %s" % (subtype, self.__class__)

		if len(self.properties) != len(args):
			raise TypeError("The args where not correct, they should be of length %s" % len(self.properties))

		for property, arg in zip(self.properties, args):
			self.length += property.length(arg)
			setattr(self, property.name, arg)

	def __str__(self):
		output = [Object.__str__(self)]
		for property in self.properties:
			arg = list(getattr(self, property.name))
			output.append(property.pack(arg))
			
		return "".join(output)

	def __repr__(self):
		return "<netlib.objects.ObjectExtra.DynamicObject - %s @ %s>" % (self._name, hex(id(self)))

	def __process__(self, leftover, **kw):
		moreargs = []

		# Unpack the described data
		for property in self.properties:
			args, leftover = property.unpack(leftover)
			moreargs.append(args)

		if len(leftover) > 0:
			raise ValueError("\nError when processing %s.\nExtra data found: %r " % (self.__class__, leftover))

		args = [self.id, self.subtype, self.name, self.desc, self.parent, self.contains, self.modify_time]
		self.__init__(self.sequence, *(args + moreargs))

class ObjectDesc(Description):
	"""\
	The OrderDesc packet consists of:
		* a UInt32, order type
		* a String, name
		* a String, description
		* a UInt64, the last time the description was modified
		* a list of
			* a UInt32, argument id?!?
			* a String, argument name
			* a String, description
			* extra data....... (described by argument id)
	"""
	no = 68
	struct="I SS T [ISS[x]]"

	@staticmethod
	def struct_callback(s):
		(name, id, description), s = unpack('SIS', s)

		if ObjectParamsStructDesc.has_key(id):
			output_extra = {}
			for substruct, ename, edescription in ObjectParamsStructDesc[id]:
				o, s = unpack(substruct, s)
				output_extra[ename] = o
			output = [name, id, description, output_extra]
		else:
			output = [name, id, description, {}]

		return output, s

	@staticmethod
	def pack_callback(arg):
		output = ""
		for name, id, description, extra in arg:
			extra = dict(extra)
			output += pack('SIS', name, id, description)
			if ObjectParamsStructDesc.has_key(id):
				for substruct, name, description in ObjectParamsStructDesc[id]:
					output += pack(substruct, extra.pop(name))

			if len(extra) > 0:
				raise TypeError("There was left over extra stuff...")
		return output

	def __init__(self, sequence, \
			id, name, description, modify_time, \
			arguments):
		Description.__init__(self, sequence, id)

		self._name = name
		self.description = description
		self.arguments = arguments
		self.modify_time = modify_time

		self.length = 4 + \
			4 + len(name) + \
			4 + len(description) + \
			4 + 8 

		# FIXME: This ignores the extradata stuff
		for argument in arguments:
			self.length += \
				4 + \
				4 + len(argument[1]) + \
				4 + len(argument[2])

	def __str__(self):
		output = Description.__str__(self)
		output += pack(self.struct, \
				self.id, \
				self._name, \
				self.description, \
				self.modify_time, \
				self.arguments,
				callback=self.pack_callback)

		return output

	def build(self):
		"""\
		*Internal*

		Builds a class from this description.
		"""
		class DynamicObject(DynamicBaseObject):
			pass

		DynamicObject._name = self._name
		DynamicObject.doc = self.description

		# Arguments
		DynamicObject.subtype = self.id
		DynamicObject.substruct = ""

		DynamicObject.properties = []
		for grouptype, groupname, groupdesc, groupparts in self.arguments:

			structures = []
			for name, type, desc, extra in groupparts:
				structures.append(ObjectParamsMapping[type](name=name, desc=desc))

				for ename, evalue in extra.items():
					setattr(structures[-1], ename, evalue)

			property = GroupStructure(groupname, groupdesc, structures=structures)

			DynamicObject.properties.append(property)
			setattr(DynamicObject, groupname, property)


		DynamicObject.modify_time = self.modify_time
		DynamicObject.packet = self

		return DynamicObject

	def register(self):
		descriptions(self.build())

__all__ = ["descriptions", "ObjectDesc"]
