from Get import Get

class Object_GetById(Get):
	"""\
	The Object_Get packet consists of:
		* A SInt32, ID of object to get.
	"""
	no = 5

