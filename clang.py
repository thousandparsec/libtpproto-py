

class AND:
	pass
	
class OR:
	pass

class NOT:
	pass

class Category:
	def __init__(self, id, number):
		self.id = id
		self.number = number

class Component:
	def __init__(self, id, number):
		self.id = id
		self.number = number

def decode(list):
	r = []
	for o, n, i in list:
		if o == 0:
			pass
		elif o == 1:
			r.append(Component(i, n))
		elif o == 2:
			r.append(Category(i, n))
		elif o == 3:
			r.append(AND())
		elif o == 4:
			r.append(OR())
		elif o == 5:
			r.append(NOT())
	return r

