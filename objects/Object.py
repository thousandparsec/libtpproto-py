
from xstruct import pack

from Header import Processed

class Object(Processed):
	"""\
	The Login packet consists of:
		 4 * a uint32, object ID
		 4 * a uint32, object type
		   * a text string, name of object
		 8 * a uint64, size of object (diameter)
		24 * 3 by int64, position of object
		24 * 3 by int64, velocity of object
		   * a list of uint32, object IDs of objects contained in the current object
		   * a list of uint32, order types that the player can send to this object
		 4 * a uint32, number of orders currently on this object
		16 * 4 by uint32 of padding, for future expansion of common attributes
		   * extra data, as defined by each object type
	"""

	no = 7
	struct = "IIS Q 3Q 3Q [I] [I] I 16x"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			*extra):
		Processed.__init__(self, sequence)

		# Length is:
		#  *  8 bytes
		#  *  4 bytes + len(name) + 1 bytes
		#  *  8 bytes
		#  * 24 bytes
		#  * 24 bytes
		#  *  4 bytes + len(contains)*4
		#  *  4 bytes + len(order_types)*4
		#  *  4 bytes
		#  * 16 bytes
		if not hasattr(self, 'length'):
			self.length = \
				4 + 4 + \
				4 + len(name) + 1 + \
				8 + 24 + 24 + \
				4 + len(contains)*4 + \
				4 + len(order_types)*4 + \
				4 + 16

		self.id = id
		self.otype = type
		self.name = name
		self.size = size
		self.pos = (posx, posy, posz)
		self.vel = (velx, vely, velz)
		self.contains = contains
		self.order_types = order_types
		self.order_number = order_number

		self.extra = extra

	def __repr__(self):
		output = Processed.__repr__(self)
		# struct = "IIS Q 3Q 3Q [I] [I] I 16x"
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
				self.order_number)
		return output

