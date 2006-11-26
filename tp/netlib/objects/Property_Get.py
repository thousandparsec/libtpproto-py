from Base import GetWithID

class Property_Get(GetWithID):
	"""\
	The Property_Get packet consists of:
		* A SInt32, ID of property to get.
	"""
	no = 58

