from Structures import *
class OrderParamAbsSpaceCoords(GroupStructure):
	"""\
	Coordinates in absolute space. (Relative to the center of the Universe)
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			GroupStructure('coordinates', 'No description', structures=[
					IntegerStructure('x', 'No description', size=64, type='signed'),
					IntegerStructure('y', 'No description', size=64, type='signed'),
					IntegerStructure('z', 'No description', size=64, type='signed'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamTime(GroupStructure):
	"""\
	The number of turns before something happens.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('turns', 'Number of turns', size=32, type='signed'),
			IntegerStructure('maxtime', 'Maximum number of turns', size=32, type='signed'),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamObject(GroupStructure):
	"""\
	An object's ID number.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('objectid', "The object's Id number.", size=32, type='unsigned'),
			ListStructure('validtypes', 'List of the valid object types which can be chosen.', structures=[
					IntegerStructure('validtype', 'A valid object type for the chosen Object ID.', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamPlayer(GroupStructure):
	"""\
	A player's ID number.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('playerid', "The player's Id number.", size=32, type='unsigned'),
			EnumerationStructure('mask', 'Mask for not allowed player Ids (On bits are NOT allowed to be chosen)', values={
					0x01 : 'allies',
					0x02 : 'tradingpartners',
					0x04 : 'neutral',
					0x08 : 'enemies',
					0x10 : 'nonplayers',
				}),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamRelSpaceCoords(GroupStructure):
	"""\
	Coordinates relative to an object
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('objectid', "The object's Id number.", size=32, type='unsigned'),
			GroupStructure('relpos', 'No description', structures=[
					IntegerStructure('x', 'No description', size=64, type='signed'),
					IntegerStructure('y', 'No description', size=64, type='signed'),
					IntegerStructure('z', 'No description', size=64, type='signed'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamRange(GroupStructure):
	"""\
	A number value from a range.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('value', 'The Value', size=32, type='signed'),
			IntegerStructure('minvalue', 'The minimum value the value can take', size=32, type='signed'),
			IntegerStructure('maxvalue', 'The maximum value the value can take', size=32, type='signed'),
			IntegerStructure('increment', 'The amount to increment by (resolution)', size=32, type='signed'),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamList(GroupStructure):
	"""\
	A in which numerous items can be selected.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('possibleselections', 'A list of the items which can be chosen.', structures=[
					IntegerStructure('id', 'ID of what can be selected', size=32, type='unsigned'),
					StringStructure('name', 'The name of the item'),
					IntegerStructure('maxnum', 'The maximum number of this item which can be selected', size=32, type='unsigned'),
				]),
			ListStructure('selection', 'A list of the items which have been selected.', structures=[
					IntegerStructure('id', 'ID of what is selected', size=32, type='unsigned'),
					IntegerStructure('number', 'The number of this item which have been selected', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamString(GroupStructure):
	"""\
	A textual string.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('maxlength', 'The maximum length of the string', size=32, type='unsigned'),
			StringStructure('string', 'No description'),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamReference(GroupStructure):
	"""\
	A reference to something.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('reference', 'The generic reference to something.', size=32, type='unsigned'),
			ListStructure('allowed', 'A list of allowed valid reference types.', structures=[
					IntegerStructure('reftype', 'Valid reference type', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamReferenceList(GroupStructure):
	"""\
	A list of references to something.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('references', 'The list of references.', structures=[
					IntegerStructure('reference', 'The generic reference to something.', size=32, type='unsigned'),
				]),
			ListStructure('allowed', 'A list of allowed valid reference types.', structures=[
					IntegerStructure('reftype', 'Valid reference type', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamResourceList(GroupStructure):
	"""\
	A list of resources to be deal with by the order.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('allowed', 'The list of possible resources and allowable maximums.', structures=[
					IntegerStructure('resourcetype', 'An allowed resource type', size=32, type='unsigned'),
					IntegerStructure('max', 'The maximum quantity allowed for this resource type.', size=32, type='unsigned'),
				]),
			IntegerStructure('maxmass', 'The maximum mass allowed.', size=32, type='unsigned'),
			IntegerStructure('maxvolument', 'The maximum volume allowed.', size=32, type='unsigned'),
			ListStructure('selected', 'The list of the selected Resources and quantities.', structures=[
					IntegerStructure('resourcetype', 'A selected resource type', size=32, type='unsigned'),
					IntegerStructure('quantity', 'The selected quantity of this resource type.', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class OrderParamGenericReferenceQuantityList(GroupStructure):
	"""\
	A quantity selection list of generic references.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('weightmaximums', 'Defines the maximums for the various weights.', structures=[
					IntegerStructure('max', 'The maximum for the given this weight.', size=32, type='unsigned'),
					ListStructure('reflist', 'The list of references that this weight limit refers to.', structures=[
							IntegerStructure('reftype', 'type of thing being referenced', size=32, type='signed'),
							IntegerStructure('refid', 'The ID of the thing referenced', size=32, type='unsigned'),
						]),
				]),
			ListStructure('possibles', 'This list defines the types of things that can be selected, weights and maximums.', structures=[
					IntegerStructure('optionid', 'The id that is option has.', size=32, type='unsigned'),
					StringStructure('name', 'The name of this option.'),
					IntegerStructure('max', 'The maximum that can be selected', size=32, type='semisigned'),
					ListStructure('reflist', 'The list of references that this option refers to.', structures=[
							IntegerStructure('reftype', 'type of thing being referenced', size=32, type='signed'),
							IntegerStructure('refid', 'The ID of the thing referenced', size=32, type='unsigned'),
						]),
					ListStructure('weights', 'The list of weights for this option.', structures=[
							IntegerStructure('weight', 'The weight for this option for the corresponding maximum weight in the same position in the list.', size=32, type='unsigned'),
						]),
				]),
			ListStructure('selection', 'A list of the items which have been selected.', structures=[
					IntegerStructure('id', 'ID of what is selected', size=32, type='unsigned'),
					IntegerStructure('number', 'The number of this item which have been selected', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)


OrderParamsStructDesc = \
		{}

OrderParamsMapping = {
		0: OrderParamAbsSpaceCoords,
		1: OrderParamTime,
		2: OrderParamObject,
		3: OrderParamPlayer,
		4: OrderParamRelSpaceCoords,
		5: OrderParamRange,
		6: OrderParamList,
		7: OrderParamString,
		8: OrderParamReference,
		9: OrderParamReferenceList,
		10: OrderParamResourceList,
		11: OrderParamGenericReferenceQuantityList,
	}


class ObjectParamPosition3d(GroupStructure):
	"""\
	A vector for the position.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			GroupStructure('vector', 'No description', structures=[
					IntegerStructure('x', 'No description', size=64, type='signed'),
					IntegerStructure('y', 'No description', size=64, type='signed'),
					IntegerStructure('z', 'No description', size=64, type='signed'),
				]),
			IntegerStructure('relative', 'The object ID this position is relative to.', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamVelocity3d(GroupStructure):
	"""\
	A vector for the velocity.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			GroupStructure('vector', 'No description', structures=[
					IntegerStructure('x', 'No description', size=64, type='signed'),
					IntegerStructure('y', 'No description', size=64, type='signed'),
					IntegerStructure('z', 'No description', size=64, type='signed'),
				]),
			IntegerStructure('relative', 'The object ID this vector is relative to.', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamAcceleration3d(GroupStructure):
	"""\
	A vector for the acceleration.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			GroupStructure('vector', 'No description', structures=[
					IntegerStructure('x', 'No description', size=64, type='signed'),
					IntegerStructure('y', 'No description', size=64, type='signed'),
					IntegerStructure('z', 'No description', size=64, type='signed'),
				]),
			IntegerStructure('relative', 'The object ID this vector is relative to.', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamBoundPosition(GroupStructure):
	"""\
	Object is bound to ('in') an Object.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('slot', 'The slot in the parent object this object is in.', size=32, type='signed'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamOrderQueue(GroupStructure):
	"""\
	An order queue.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('queueid', 'The ID number of the queue.', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamResourceList(GroupStructure):
	"""\
	A list of resources.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('resources', 'A list of resources.', structures=[
					IntegerStructure('resourceid', 'The Resource ID', size=32, type='unsigned'),
					IntegerStructure('stored', 'The amount on hand currently.', size=32, type='unsigned'),
					IntegerStructure('minable', 'The amount of the resource that is minable or creatable.', size=32, type='unsigned'),
					IntegerStructure('unavailable', 'The amount that is not yet minable or creatable.', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParmReference(GroupStructure):
	"""\
	A generic reference to something.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('type', 'type of thing being referenced', size=32, type='signed'),
			IntegerStructure('id', 'No description', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamReferenceQuantityList(GroupStructure):
	"""\
	Gives a list of references and how many of each of them.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			ListStructure('references', 'A list of as described in the Generic Reference System', structures=[
					IntegerStructure('type', 'type of thing being referenced', size=32, type='signed'),
					IntegerStructure('id', 'No description', size=32, type='unsigned'),
					IntegerStructure('number', 'No description', size=32, type='unsigned'),
				]),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamInteger(GroupStructure):
	"""\
	An Integer, informational.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('value', 'The value of the integer parameter.', size=32, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamSize(GroupStructure):
	"""\
	The diameter of the object.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			IntegerStructure('size', 'The size of the object (diameter).', size=64, type='unsigned'),
		]
		GroupStructure.__init__(self, *args, **kw)

class ObjectParamMedia(GroupStructure):
	"""\
	The url for the media for this object, either relative to the base url given in the Game frame, of absolute.
	"""
	def __init__(self, *args, **kw):
		kw['structures'] = [
			StringStructure('url', 'The url for the media.'),
		]
		GroupStructure.__init__(self, *args, **kw)


ObjectParamsStructDesc = {}
ObjectParamsMapping = {
		0: ObjectParamPosition3d,
		1: ObjectParamVelocity3d,
		2: ObjectParamAcceleration3d,
		3: ObjectParamBoundPosition,
		4: ObjectParamOrderQueue,
		5: ObjectParamResourceList,
		6: ObjectParmReference,
		7: ObjectParamReferenceQuantityList,
		8: ObjectParamInteger,
		9: ObjectParamSize,
		10: ObjectParamMedia,
	}
