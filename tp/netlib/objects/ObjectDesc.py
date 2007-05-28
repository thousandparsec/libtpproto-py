
import sys
import site
import string
import os
from os import path

def splitall(p, extra = []):
	bits = []
	while not p in ['', '..', '.'] \
		and not p in getattr(site, 'sitedirs', ()) \
		and not p in sys.path \
		and not p in extra:
		p, c = os.path.split(p)
		bits.append(c)
	bits.reverse()
	return bits	

def edir(p):
	extra = path.splitext(path.basename(p))[0][:-4] + "Extra"
	d = path.join(path.dirname(p), extra)

	return d

def import_subtype(p, py2exe=None, installer=None):
	subtypes = {}

	if py2exe != None:
		paths = splitall(p, py2exe.archive)
	elif installer != None:
		paths = p.split(".")
	else:
		paths = splitall(p)
	import_base = string.join(paths, ".")

	if py2exe != None:
		files = []
		for thing in py2exe._files.values():
			file = thing[0]
			if p in file:
				files.append(file)
	elif installer != None:
		files = []
		for file in installer:
			if file.startswith(import_base + "."):
				files.append(file[len(import_base)+1:] + ".py")
	else:
		files = os.listdir(p)

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
def descriptions(added=None):
	global _descriptions

	if _descriptions == None:
		try:
			_descriptions = import_subtype(edir(__file__), py2exe=__loader__)
		except NameError, e:
			try:
				import sys
				if sys.frozen == "macosx_app":
					raise AttributeError("macosx_app")
				print sys.frozen
				import carchive
				this = carchive.CArchive(sys.executable).openEmbeddedZlib("out1.pyz")
				_descriptions = import_subtype("tp.netlib.objects.ObjectExtra", installer=this.contents())
			except AttributeError, e:
				_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
	
	return _descriptions
