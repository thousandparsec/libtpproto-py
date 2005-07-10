from Base import GetWithID

class Design_Remove(GetWithID):
	"""\
	The Design_Remove packet consists of:
		* A SInt32, ID of design to remove.
	"""
	no = 51

