
import site
import string
import os
from os import path

def splitall(p, extra = []):
	bits = []
	while not p in ['', '..', '.'] and not p in site.sitedirs and not p in extra:
		p, c = os.path.split(p)
		bits.append(c)
	bits.reverse()
	return bits	

def edir(p):
	extra = path.splitext(path.basename(p))[0][:-4] + "Extra"
	d = path.join(path.dirname(p), extra)

	return d

def import_subtype(p, loader=None):
	subtypes = {}

	if loader == None:
		paths = splitall(p)
	else:
		paths = splitall(p, loader.archive)
	import_base = string.join(paths, ".")

	if loader == None:
		files = os.listdir(p)
	else:
		files = []
		for thing in loader._files.values():
			file = thing[0]
			if p in file:
				files.append(file)

	for file in files:
		name, ext = path.splitext(path.basename(file))
		if not ext in [".py", ".pyc", ".pyo"] or name == "__init__":
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
		try:
			_descriptions = import_subtype(edir(__file__), __loader__)
		except NameError:
			_descriptions = import_subtype(edir(__file__))
		
	return _descriptions
