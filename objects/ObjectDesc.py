
import string
import os
from os import path

def splitall(p):
	bits = []
	while p != '':
		p, c = os.path.split(p)
		if c == ".." or c == ".":
			break
		bits.append(c)
	bits.reverse()
	return bits	

def edir(p):
	extra = path.splitext(path.basename(p))[0][:-4] + "Extra"
	d = path.join(path.dirname(p), extra)

	return d

def import_subtype(p):
	subtypes = {}
	import_base = string.join(splitall(p), ".")
	
	for file in os.listdir(p):
		name, ext = path.splitext(path.basename(file))
		if ext != ".py" or name == "__init__":
			continue
			
		try:
			s = "from %s import %s\nlib = %s" % (import_base, name, name)
			exec(s)
#			lib = __import__("%s.%s" % (import_base, name), globals(), locals(), [name])
		except ImportError, e:
			print "Import Error", e

		if not hasattr(lib, name):
			continue
		
		cl = getattr(lib, name)
		if not hasattr(cl, "subtype"):
			continue
			
		if subtypes.has_key(cl.subtype):
			continue
		
		subtypes[cl.subtype] = cl

	return subtypes

_descriptions = None
def descriptions():
	global _descriptions

	if _descriptions == None:
		_descriptions = import_subtype(edir(__file__))
	return _descriptions
