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


class Parser(object):

	def CreateParser(cls):
		return cls()
	CreateParser = classmethod(CreateParser)

	def ParseFile(self, file):
		tree = ET.parse(file)
		self.root = tree.getroot()


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
						structuse[id] = []
						for struct in child.getchildren()[0].getchildren():
							structuse[id].append(tag2struct(struct))

					if child.tag == "descstruct":
						structdesc[id] = []
						for struct in child.getchildren()[0].getchildren():
							structdesc[id].append(tag2struct(struct))

			print "%sName = \\" % (parameterset.attrib['name'])
			print "\t\t" + pprint.pformat(names).replace('\n', '\n\t\t')
			print
			print "%sDesc = \\" % (parameterset.attrib['name'])
			print "\t\t" + pprint.pformat(descs).replace('\n', '\n\t\t')
			print
			print "%sStructUse = \\" % (parameterset.attrib['name'])
			print "\t\t" + pprint.pformat(structuse).replace('\n', '\n\t\t')
			print
			print "%sStructDesc = \\" % (parameterset.attrib['name'])
			print "\t\t" + pprint.pformat(structdesc).replace('\n', '\n\t\t')
			print
			print

if __name__ == "__main__":
	
	parser = Parser.CreateParser()
	parser.ParseFile(file("protocol.xml", "r"))




