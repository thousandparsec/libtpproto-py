
from xstruct import pack
from objects import Object

class Planet(Object):
	"""\
	A planet is any body in space which is very large and naturally occuring.

	*  a SInt32, the id of the player who "owns" this planet or -1 if not owned or unknown
	* a list of,
		* a UInt32, the resource id
		* a UInt32, the units of this resource on the "surface"
		* a UInt32, the maximum units of this resource remaining which are minable
		* a UInt32, the maximum units of this resource remaining which are inaccessable
	"""
	subtype = 3
	substruct = "j[jjjj]"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			owner, resources):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time)

		self.length += 4 + 4 + 16 * len(resources)
		self.owner = owner

		for r in resources:
			if len(r) != 4:
				raise TypeError("Resources should be 4 length, <id> <surface> <minable> <inaccess>")

		self.resources = resources
	
	def __str__(self):
		output = Object.__str__(self)
		output += pack(self.substruct, self.owner, self.resources)

		return output
