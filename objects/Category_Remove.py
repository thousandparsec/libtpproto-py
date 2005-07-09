from Base import GetWithID

class Category_Remove(GetWithID):
	"""\
	The Category_Remove packet consists of:
		* A SInt32, ID of category to remove.
	"""
	no = 44

