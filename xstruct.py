"""\
An advanced version of pack/unpack which works with extra TP strutures.

Everything is assumed to be network order, ie you don't need to
prepend every struct with !

Extra stuff defined by this module:

 S	String
 Y	Padded String	
 [	List Start	(unsigned int32 length)
 ]	List End	
 {      List Start      (unsigned int64 length)
 }      List End
 
The structure of the data in the list is described by the data inside the
brackets.

Example:
	[L] would be a list of unsigned longs
	It is actually transmitted as <length><data><data><data>
	
Obviously you can't calculate size of an xstruct string. The unpack
function will return the unused data.
"""

import pprint
import struct
import sys
import string
from types import *

_pack = struct.pack
_unpack = struct.unpack
_calcsize = struct.calcsize

def hexbyte(string):
	"""\
	Takes a string and prints out the bytes in hex.
	"""
	s = ""
	for i in string:
		s += str(hex(ord(i)))
		if ord(i) > ord('A') and ord(i) < ord('z'):
			s += "(%s)" % i
		s += " "
	return s

def pack(struct, *args):
	"""\
	Takes a structure string and the arguments to pack in the format
	specified by string.
	"""
	args = list(args)
	output = ""

	while len(struct) > 0:
		char = struct[0]
		struct = struct[1:]
		
		if char == ' ' or char == '!':
			continue
		elif char == '{':
			# Find the closing brace
			substruct, struct = string.split(struct, '}', maxsplit=1)
			output += pack_list('L', substruct, args.pop(0))
		elif char == '[':
			# Find the closing brace
			substruct, struct = string.split(struct, ']', maxsplit=1)
			output += pack_list('I', substruct, args.pop(0))
		elif char == 'S':
			output += pack_string(args.pop(0))
		elif char in string.digits:
			# Get all the numbers
			substruct = char
			while struct[0] in string.digits:
				substruct += struct[0]
				struct = struct[1:]
			# And the value the number applies to
			substruct += struct[0]
			struct = struct[1:]
			
			number = int(substruct[:-1])
			if substruct[-1] == 's':
				output += _pack("!"+substruct, args.pop(0))
			elif substruct[-1] == 'x':
				output += "\0" * number
			else:
				# Get the correct number of arguments
				new_args = []
				while len(new_args) < number:
					new_args.append(args.pop(0))
					
				output += apply(_pack, ["!"+substruct,] + new_args)
				
		else:
			output += _pack("!"+char, args.pop(0))
			
	return output


def unpack(struct, s):
	"""\
	Takes a structure string and a data string.

	((values1,value2), remaining_data)
	
	"""
	output = []
	
	while len(struct) > 0:
		char = struct[0]
		struct = struct[1:]

		if char == ' ' or char == '!':
			continue
		elif char == '{':
			# Find the closing brace
			substruct, struct = string.split(struct, '}', maxsplit=1)
			data, s = unpack_list("L", substruct, s)
			
			output.append(data)
		elif char == '[':
			# Find the closing brace
			substruct, struct = string.split(struct, ']', maxsplit=1)
			data, s = unpack_list("I", substruct, s)
			
			output.append(data)
		elif char == 'S':
			data, s = unpack_string(s)
			
			output.append(data)
		elif char in string.digits:
			# Get all the numbers
			substruct = char
			while struct[0] in string.digits:
				substruct += struct[0]
				struct = struct[1:]
			# And the value the number applies to
			substruct += struct[0]
			struct = struct[1:]
			
			size = _calcsize(substruct)
			data = _unpack("!"+substruct, s[:size])
			s = s[size:]

			output += data
		else:
			substruct = "!"+char

			size = _calcsize(substruct)

			data = _unpack(substruct, s[:size])
			s = s[size:]

			output += data

	return tuple(output), s

def pack_list(length_struct, struct, args):
	"""\
	*Internal*

	Packs the id list so it can be send.
	"""
	# The length
	output = pack(length_struct, len(args))

	# The list
	for id in args:
		if type(id) == ListType or type(id) == TupleType:
			args = [struct] + list(id)
			output += apply(pack, args)
		else:
			output += pack(struct, id)
		
	return output

def unpack_list(length_struct, struct, s):
	"""\
	*Internal*

	Returns the first string from the input data and any remaining data.
	"""
	output, s = unpack(length_struct, s)
	length, = output

	list = []
	for i in range(0, length):
		output, s = unpack(struct, s)
		if len(output) == 1:
			list.append(output[0])
		else:
			list.append(output)

	return list, s

def pack_string(s):
	"""\
	*Internal*

	Prepares a string to be send out on a wire.
	
	It appends the string length to the beginning and adds a 
	null terminator.
	"""
	temp = s + "\0"
	return pack("!I", len(temp)) + temp

def unpack_string(s):
	"""\
	*Internal*

	Returns the first string from the input data and any remaining data.
	"""
	# Totally empty string
	if len(s) == 0:
		return "", s
	
	# Remove the length
	(l, ), s = unpack("I", s)
	if l > 0:
		# Get the string, (we don't need the null terminator so nuke it)
		output = s[:l-1]
		s = s[l:]
		
		return output, s
	else:
		return "", s
