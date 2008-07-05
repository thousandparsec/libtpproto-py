import pprint

# Need to find an ElementTree implimentation!
ET = None
errors = []
try:
	import elementtree.ElementTree as ET
except ImportError, e:
	errors.append(e)
try:
	import cElementTree as ET
except ImportError:
	errors.append(e)
try:
	import lxml.etree as ET
except ImportError:
	errors.append(e)
try:
	import xml.etree.ElementTree as ET
except ImportError:
	errors.append(e)
if ET is None:
	raise ImportError(str(errors))

############################################################
# Old method for converting a node to an xstruct....
############################################################
int_size2char = {
	  8 : 'b',
	 16 : 'h',
	 32 : 'i',
	 64 : 'q',
}

int_size2semi = {
 16: 'n',
 32: 'j',
 64: 'p',
}

def tag2struct(node):
	char = None

	if node.tag == "integer":
		char = int_size2char[int(node.attrib['size'])]

		if node.attrib['type'] == "unsigned":
			char = char.upper()

		if node.attrib['type'] == "semisigned":
			char = int_size2semi[int(node.attrib['size'])]

	if node.tag == "string":
		char = "s"

	if node.tag == "list":
		char = "["
		for listchild in node.getchildren():
			if listchild.tag != "structure":
				continue

			for struct in listchild.getchildren():
				char += tag2struct(struct)[0]
			
		char += "]"

	if node.tag == "group":
		char = ""

		for groupchild in node.getchildren():
			if groupchild.tag != "structure":
				continue

			for struct in groupchild.getchildren():
				char += tag2struct(struct)[0]

	if node.tag == "enumeration":
		char = "I"

	name = None
	desc = None
	for child in node.getchildren():
		if child.tag == "name":
			name = child.text.strip()
		if child.tag == "description":
			desc = child.text.strip()
	return (char, name, desc) 

############################################################
# New method for printing out the properties......
############################################################

def PrinterFactory(node, indent=0):
	if node.tag == "integer":
		return IntegerPrinter(node, indent=indent+1)
	if node.tag == "list":
		return ListPrinter(node, indent=indent+1)
	if node.tag == "group":
		return GroupPrinter(node, indent=indent+1)
	if node.tag == "string":
		return StringPrinter(node, indent=indent+1)
	if node.tag == "enumeration":
		return EnumerationPrinter(node, indent=indent+1)
	return BasePrinter(node, indent=indent+1)

class BasePrinter(object):
	template = """%(type)sStructure(%(name)r, %(desc)r%(extra)s)"""
	def __init__(self, node, indent=0):
		self.type = self.__class__.__name__[:-7]
		self.indent = indent

		self.name = ""
		self.desc = "No description"
		for child in node.getchildren():
			if child.tag == "name":
				self.name = child.text.strip()
			if child.tag == "description":
				self.desc = child.text.strip()
		self.extra = ""

	def __repr__(self):
		return self.template % self.__dict__

class StringPrinter(BasePrinter):
	pass

class IntegerPrinter(BasePrinter):
	def __init__(self, node, indent=0):
		BasePrinter.__init__(self, node, indent=0)
		if not "size" in node.attrib:
			node.attrib['size'] = 32
		if not "type" in node.attrib:
			node.type['type'] = "signed"
		self.extra = ", size=%(size)s, type=%(type)r" % node.attrib

class GroupPrinter(BasePrinter):
	def __init__(self, node, indent=0):
		BasePrinter.__init__(self, node, indent)

		self.structures = []
		for listchild in node.getchildren():
			if listchild.tag != "structure":
				continue

			for struct in listchild.getchildren():
				self.structures.append(PrinterFactory(struct, self.indent))

		wrapped = "[\n"
		for s in self.structures:
			wrapped += "\t\t\t" + "\t\t" * self.indent + "%r,\n" % s
		wrapped += "\t\t" + "\t\t" * self.indent + "]"

		self.extra = ", structures=%s" % wrapped

class ListPrinter(GroupPrinter):
	pass

class EnumerationPrinter(IntegerPrinter):
	def __init__(self, node, indent):
		IntegerPrinter.__init__(self, node, indent)

		self.values = []
		for struct in node.getchildren():
			if struct.tag != "values":
				continue
			for struct in struct.getchildren():
				self.values.append((struct.attrib['id'], struct.attrib['name']))

		wrapped = "{\n"
		for t in self.values:
			wrapped += "\t\t\t\t\t" + "\t\t" * self.indent + "%s : %r,\n" % t
		wrapped += "\t\t\t\t" + "\t\t" * self.indent + "}"
		self.extra = ", values=%s" % wrapped

class PropertyPrinter(object):
	template = """\
class %(name)s(GroupStructure):
	""\"\\
%(desc)s
	""\"
	def __init__(self, *args, **kw):
		kw['structures'] = [%(s)s
		]
		GroupStructure.__init__(self, *args, **kw)
"""
	def __init__(self, name, desc):
		self.name = name[0].upper() + name[1:]
		self.desc = "\t" +desc.replace("\n", "\n\t")
		self.structures = []

	def addproperty(self, node):
		self.structures.append(PrinterFactory(node))

	def __repr__(self):
		self.s = ""
		for s in self.structures:
			self.s +="\n\t\t\t%r,""" % s
		return self.template % self.__dict__

############################################################
############################################################

class Parser(object):

	def CreateParser(cls):
		return cls()
	CreateParser = classmethod(CreateParser)

	def ParseFile(self, file):
		tree = ET.parse(file)
		self.root = tree.getroot()

		print "from Structures import *"

		for parameterset in self.root.getchildren():
			if parameterset.tag != "parameterset":
				continue

			names      = {}
			descs      = {}
			structuse  = {}
			structdesc = {}

			for parameter in parameterset.getchildren():
				if parameter.tag != "parameter":
					continue
			
				id = int(parameter.attrib['type'])

				names[id] = parameter.attrib['name']

				for child in parameter.getchildren():
					if child.tag == "description":
						descs[id] = child.text.strip()
						
					if child.tag == "usestruct":
						structuse[id] = PropertyPrinter(parameter.attrib['name'], descs[id])

						for struct in child.getchildren()[0].getchildren():
							structuse[id].addproperty(struct)

					if child.tag == "descstruct":
						structdesc[id] = []
						for struct in child.getchildren()[0].getchildren():
							structdesc[id].append(tag2struct(struct))

			for i, k in structuse.items():
				print k

			print
			print "%sStructDesc = \\" % (parameterset.attrib['name'])
			print "\t\t" + pprint.pformat(structdesc).replace('\n', '\n\t\t')
			print
			print "%sMapping = {" % (parameterset.attrib['name'])
			for id, name in names.items():
				print "\t\t%s: %s," % (id, name[0].upper()+name[1:])
			print "\t}"
			print
			print

if __name__ == "__main__":
	
	parser = Parser.CreateParser()
	parser.ParseFile(file("protocol.xml", "r"))

