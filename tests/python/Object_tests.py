
import string
import sys
import traceback

import objects

from xstruct import hexbyte

# Hand built Object packet

id = 22
otype = 2
name = "Hand Build Object"
size = 100
pos = (8, 20, 10)
vel = (1, 4, 35)
contains = [10, 5, 24, 11, 2]
order_types = [2, 22, 10]
order_number = 2

header = "TP02" +  "\0\0\0\26" +  "\0\0\0\7" + "\x00\x00\x00\x96" 
data = "\0\0\0\26" + \
	"\0\0\0\2" + \
	"\0\0\0\22" + name + "\0" + \
	"\0\0\0\0\0\0\0\144" + \
	"\0\0\0\0\0\0\0\10" + "\0\0\0\0\0\0\0\24" + "\0\0\0\0\0\0\0\12" + \
	"\0\0\0\0\0\0\0\1" + "\0\0\0\0\0\0\0\4" + "\0\0\0\0\0\0\0\43" + \
	"\0\0\0\5" + "\0\0\0\12" + "\0\0\0\5" + "\0\0\0\30" + "\0\0\0\13" + "\0\0\0\2" + \
	"\0\0\0\3" + "\0\0\0\2" + "\0\0\0\26" + "\0\0\0\12" + \
	"\0\0\0\2" + \
	"\0\0\0\0" + "\0\0\0\0" + "\0\0\0\0" + "\0\0\0\0" + \
	"\1\2\4\5"


def get_traceback():
	type, val, tb = sys.exc_info()
	return string.join(traceback.format_exception(type, val, tb), '')

def test(p):
	# Check the class
	if not isinstance(p, objects.Object):
		return False, "The Frame type was incorrect after processing\nClass: %s\n" % (p.__class__)

	# Check the sequence number
	if p.sequence != 22:
		return False, "The Frame sequence number was incorrect\nCorrect: '22'\nActual: '%s'\n" % (p.sequence)

	# Check the length
	if p.length != len(data):
		return False, "The Frame data length was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (len(data), p.length)
	
	# Check the data
	if p.id != id:
		return False, "The Frame data (id) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (id, p.id)
	if p.otype != otype:
		return False, "The Frame data (type) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (otype, p.otype)
	if p.name != name:
		return False, "The Frame data (name) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (name, p.name)
	if p.size != size:
		return False, "The Frame data (size) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (size, p.size)
	if p.pos != pos:
		return False, "The Frame data (pos) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (pos, p.pos)
	if p.vel != vel:
		return False, "The Frame data (vel) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (vel, p.vel)
	if p.contains != contains:
		return False, "The Frame data (contains) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (contains, p.contains)
	if p.order_types != order_types:
		return False, "The Frame data (order_types) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (order_types, p.order_types)
	if p.order_number != order_number:
		return False, "The Frame data (order_number) was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (order_number, p.order_number)

	return True, None

def test1():
	"""\
	Tests if Object can be built using Header(header) and process(data)
	"""

	try:
		p = objects.Header(header)
	except:
		return False, "Exception on creation with header\n%s\n" % get_traceback()

	if (not isinstance(p, objects.Header)) or issubclass(p.__class__, objects.Processed):
		return False, "The Frames type was incorrect after header\n Class: %s\n" % (p.__class_)
		
	# This should cause an exception
	try:
		p.type
		return False, "Was allowed to get stuff before processing\n"
	except AttributeError:
		pass
	
	try:
		p.process(data)
	except:
		return False, "Exception on processing with data\n%s\n" % get_traceback()

	return test(p)



def test2():
	"""\
	Tests if Object can be built using Header(header+data)
	"""
	try:
		p = objects.Header(header+data)
	except:
		return False, "Exception on creation with header+data\n%s\n" % get_traceback()


	return test(p)

def test3():
	"""\
	Check that creating an object produces correct results.
	"""
	try:
		p = objects.Object(22, \
				id, otype, name, size, \
				pos[0], pos[1], pos[2], \
				vel[0], vel[1], vel[2], \
				contains, order_types, order_number \
			)
	except:
		return False, "Exception on creation with varibles\n%s\n" % get_traceback()
		
	return test(p)

def test4():
	"""\
	Check repr produces the correct string.
	"""

	p = objects.Object(22, \
			id, otype, name, size, \
			pos[0], pos[1], pos[2], \
			vel[0], vel[1], vel[2], \
			contains, order_types, order_number \
		)
	d = repr(p)

	# This should produce data the same as our string
	if d != header+data:
		return False, "Data is not the same as home produced\nCorrect: '%s'\nActual: '%s'\n" % \
			(hexbyte(header+data), hexbyte(d))

	return True, None

tests = [test1, test2, test3, test4]

