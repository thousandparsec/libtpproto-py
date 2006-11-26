from Base import GetWithID

class Design_Get(GetWithID):
	"""\
	The Design_Get packet consists of:
		* A SInt32, ID of design to get.
	"""
	no = 47

