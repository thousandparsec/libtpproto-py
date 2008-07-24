from Base import GetWithID

class CommandDesc_Get(GetWithID):
	"""\
	The CommandDesc_Get packet consists of:
		* A UInt32, ID of object to get.
	"""
	no = 1002

