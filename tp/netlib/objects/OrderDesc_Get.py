from Base import GetWithID

class OrderDesc_Get(GetWithID):
	"""\
	The Object_Get packet consists of:
		* A UInt32, ID of object to get.
	"""
	no = 8

