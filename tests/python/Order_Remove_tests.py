
import string
import sys
import traceback

import objects

# Hand built Order_Remove packet
# TP02<32><0><><0>
# BTW These numbers \<> are in octal

header = "TP02" +  "\0\0\0\0" +  "\0\0\0\15" + "\0\0\0\20" 
data = "\0\0\0\3" + "\0\0\0\2" + "\0\0\0\1" + "\0\0\0\3"

oid = 3
slots = [1, 3]

def get_traceback():
	type, val, tb = sys.exc_info()
	return string.join(traceback.format_exception(type, val, tb), '')

def test(p):
	# Check the class
	if not isinstance(p, objects.Order_Remove):
		return False, "The Frame type was incorrect after processing\nClass: %s\n" % (p.__class__)

	# Check the sequence number
	if p.sequence != 0:
		return False, "The Frame sequence number was incorrect\nCorrect: 0\nActual: %s\n" % (p.sequence)

	# Check the length
	if p.length != len(data):
		return False, "The Frame data length was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (len(data), p.length)
	
	# Check the data
	if p.oid != oid:
		return False, "The Frame data was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (oid, p.oid)
	if p.slots != slots:
		return False, "The Frame data was incorrect\nCorrect: '%s'\nActual: '%s'\n" % (slots, p.slots) 

	return True, None

def test1():
	"""\
	Tests if Object_GetById can be built using Header(header) and process(data)
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
	Tests if Object_GetById can be built using Header(header+data)
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
		p = objects.Order_Remove(0, oid, slots)
	except:
		return False, "Exception on creation with varibles\n%s\n" % get_traceback()
		
	return test(p)

def test4():
	"""\
	Check repr produces the correct string.
	"""

	p = objects.Order_Remove(0, oid, slots)
	d = repr(p)

	# This should produce data the same as our string
	if d != header+data:
		return False, "Data is not the same as home produced\nCorrect: '%s'\nActual: '%s'\n" % \
			(hexbyte(header+data), hexbyte(d))

	return True, None

tests = [test1, test2, test3, test4]

