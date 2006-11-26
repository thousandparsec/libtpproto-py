from Base import GetWithID

class Object_GetById(GetWithID):
	"""\
	The Object_Get packet consists of:
		* A SInt32, ID of object to get.
	"""
	no = 5

