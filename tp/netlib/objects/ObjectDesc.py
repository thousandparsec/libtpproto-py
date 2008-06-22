
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
from ObjectDesc import *
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

from parameters import ObjectParamsStructUse, ObjectParamsStructDesc, ObjectParamsName
class DynamicBaseObject(Object):
	"""\
	An Object Type built by a ObjectDesc.
	"""
	substruct = ""
	subtype = -1
	name = "Base"

	__metaclass__ = ClassNicePrint

	ARG_STRUCTMAP = ObjectParamsStructUse
	ARG_NAMEMAP   = ObjectParamsName

	def __init__(self, sequence, \
			id, subtype, name, \
			desc, \
			parent, \
			contains, \
			modify_time, \
			*args, **kw):
		Object.__init__(self, sequence, id, subtype, name, desc, parent, contains, modify_time)

		assert subtype == self.subtype, "Type %s does not match this class %s" % (subtype, self.__class__)

		args = list(args)
		for name, type in self.names:
			setattr(self, name, args[0])
			args.pop(0)

		# FIXME: Need to figure out the length a better way
		self.length = len(self.__str__()) - Header.size

	def __str__(self):
		output = [Object.__str__(self)]
		for name, type in self.names:
			args = list(getattr(self, name))

			for struct, typename, typedesc in self.ARG_STRUCTMAP[type]:
				structargs = args[0]
				output.append(pack(struct, *structargs))
				args.pop(0)
			
		return "".join(output)

	def __repr__(self):
		return "<netlib.objects.ObjectExtra.DynamicObject - %s @ %s>" % (self._name, hex(id(self)))

	def __process__(self, leftover, **kw):
		moreargs = []
		# Unpack the described data
		for name, type in self.names:
			
			moreargs.append([])
			for struct, typename, typedesc in self.ARG_STRUCTMAP[type]:
				structargs, leftover = unpack(struct, leftover)
				moreargs[-1].append(structargs)

		if len(leftover) > 0:
			raise ValueError("\nError when processing %s.\nExtra data found: %r " % (self.__class__, leftover))

		args = [self.id, self.subtype, self.name, self.desc, self.parent, self.contains, self.modify_time]
		self.__init__(self.sequence, *(args + moreargs))

class Group(object):
	"""\
	Base class for a group of Properties
	"""
	pass

class ObjectDesc(Description):
	"""\
	The OrderDesc packet consists of:
		* a UInt32, order type
		* a String, name
		* a String, description
		* a UInt64, the last time the description was modified
		* a list of
			* a UInt32, argument type
			* a String, argument name
			* a String, description

	IE
	ID: 1001
	Name: Drink With Friends
	Description: Go to the pub and drink with friends.
	Arguments:
		Name: How Long
		Type: ARG_TIME
		Description: How many turns to drink for.

		Name: Who With
		Type: ARG_PLAYER
		Description: Which player to drink with.

		Name: Where
		Type: ARG_COORD
		Description: Where to go drinking.

		Name: Cargo
		Type: ARG_INT
		Description: How much beer to drink.
	"""
	no = 68
	struct="I SS T [ISS[x]]"

	@staticmethod
	def struct_callback(s):
		(name, id, description), s = unpack('SIS', s)

		if ObjectParamsStructDesc.has_key(id):
			output_extra = []
			for substruct, name, description in ObjectParamsStructDesc[id]:
				o, s = unpack(substruct, s)
				output_extra.append(o)
			output = [name, id, description, output_extra]
		else:
			output = [name, id, description, []]

		return output, s

	@staticmethod
	def pack_callback(arg):
		output = ""
		for name, id, description, extra in arg:
			print name, id, description, extra
			output += pack('SIS', name, id, description)
			if ObjectParamsStructDesc.has_key(id):
				for substruct, name, description in ObjectParamsStructDesc[id]:
					output += pack(substruct, extra.pop(0))

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

		for argument in arguments:
			self.length += \
				4 + \
				4 + len(argument[1]) + \
				4 + len(argument[2])

	def __str__(self):
		output = Description.__str__(self)
		print self.struct
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
		DynamicObject.names = []
		DynamicObject.subtype = self.id
	
		DynamicObject.substruct = ""
		for groupip, groupname, groupdesc, parts in self.arguments:
			for name, type, desc, extra in parts:
				fullname = "%s%s" % (groupname, name)

	 			DynamicObject.names.append((fullname, type))
				setattr(DynamicObject, fullname + "__doc__", desc)

		DynamicObject.modify_time = self.modify_time
		DynamicObject.packet = self

		return DynamicObject

	def register(self):
		descriptions(self.build())

__all__ = ["descriptions", "ObjectDesc"]
