from Base import GetWithID

class ObjectDesc_Get(GetWithID):
	"""\
	The ObjectDesc_Get packet consists of:
		* A UInt32, ID of object to get.
	"""
	no = 67

