from Base import GetWithID

class Category_Get(GetWithID):
	"""\
	The Category_Get packet consists of:
		* A SInt32, ID of category to get.
	"""
	no = 41

