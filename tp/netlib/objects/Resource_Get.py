from Base import GetWithID

class Resource_Get(GetWithID):
	"""\
	The Resource_Get packet consists of:
		* A list of uint32, IDs of message boards to get.
	"""
	no = 22

