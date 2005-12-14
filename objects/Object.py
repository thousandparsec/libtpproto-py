
from xstruct import pack, unpack

from Description import Describable
from ObjectDesc import descriptions

class Object(Describable):
	"""\
	The Object packet consists of:
		 4 * a UInt32, object ID
		 4 * a UInt32, object type
		   * a String, name of object
		 8 * a UInt64, size of object (diameter)
		24 * 3 by Int64, position of object
		24 * 3 by Int64, velocity of object
		   * a list of UInt32, object IDs of objects contained in the current object
		   * a list of UInt32, order types that the player can send to this object
		 4 * a UInt32, number of orders currently on this object
		   * a UInt64, the last modified time
		16 * 2 by UInt32 of padding, for future expansion of common attributes
		   * extra data, as defined by each object type
	"""

	no = 7
	struct = "IIS Q 3q 3q [I] [I] I Q 8x"

	def __init__(self, sequence, \
			id, otype, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			*args, **kw):
		Describable.__init__(self, sequence)

#		print "Object.__init__", order_number, modify_time

		if kw.has_key('extra'):
			extra = kw['extra']
		else:
			extra = None

		# Upgrade the class to the real type
		if self.__class__ == Object:
			if descriptions().has_key(otype):
				self.__class__ = descriptions()[otype]

				if extra != None or len(args) > 0:
					if extra != None:
						if len(self.substruct) > 0:
							args, leftover = unpack(self.substruct, extra)
						else:
							args = ()

				args = (self, sequence, id, otype, name, size, posx, posy, posz, 
						velx, vely, velz, contains, order_types, order_number, modify_time) + args

				apply(self.__class__.__init__, args)
				return
			else:
				# FIXME: Should throw a description error
				if extra != None:
					self.extra = extra

		struct = "IIS Q 3q 3q [I] [I] I Q 8x"
		self.length = \
			4 + 4 + \
			4 + len(name) + \
			8 + 3*8 + 3*8 + \
			4 + len(contains)*4 + \
			4 + len(order_types)*4 + \
			4 + 8 + 8

		self.id = id
		self.otype = otype
		self.name = name
		self.size = size
		self.pos = (posx, posy, posz)
		self.vel = (velx, vely, velz)
		self.contains = contains
		self.order_types = order_types
		self.order_number = order_number
		self.modify_time = modify_time

	def __str__(self):
		output = Describable.__str__(self)
		output += pack(self.struct, \
				self.id, \
				self.otype, \
				self.name, \
				self.size, \
				self.pos[0], \
				self.pos[1], \
				self.pos[2], \
				self.vel[0], \
				self.vel[1], \
				self.vel[2], \
				self.contains, \
				self.order_types, \
				self.order_number, \
				self.modify_time)
		return output

	def process_extra(self, extra):
		pass

