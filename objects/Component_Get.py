from Base import GetWithID

class Component_Get(GetWithID):
	"""\
	The Component_Get packet consists of:
		* A SInt32, ID of component to get.
	"""
	no = 1045

