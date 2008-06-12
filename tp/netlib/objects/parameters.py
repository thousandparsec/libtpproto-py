OrderParamsName = \
		{0: 'orderParamAbsSpaceCoords',
		 1: 'orderParamTime',
		 2: 'orderParamObject',
		 3: 'orderParamPlayer',
		 4: 'orderParamRelSpaceCoords',
		 5: 'orderParamRange',
		 6: 'orderParamList',
		 7: 'orderParamString',
		 8: 'orderParamReference',
		 9: 'orderParamReferenceList',
		 10: 'orderParamResourceList',
		 11: 'orderParamGenericReferenceQuantityList'}

OrderParamsDesc = \
		{0: 'Coordinates in absolute space. (Relative to the center of the Universe)',
		 1: 'The number of turns before something happens.',
		 2: "An object's ID number.",
		 3: "A player's ID number.",
		 4: 'Coordinates relative to an object',
		 5: 'A number value from a range.',
		 6: 'A in which numerous items can be selected.',
		 7: 'A textual string.',
		 8: 'A reference to something.',
		 9: 'A list of references to something.',
		 10: 'A list of resources to be deal with by the order.',
		 11: 'A quantity selection list of generic references.'}

OrderParamsStructUse = \
		{0: [('qqq', 'pos', None)],
		 1: [('i', 'turns', 'Number of turns'),
		     ('i', 'maxtime', 'Maximum number of turns')],
		 2: [('I', 'objectid', "The object's Id number."),
		     ('[I]',
		      'validtypes',
		      'List of the valid object types which can be chosen.')],
		 3: [('I', 'playerid', "The player's Id number."),
		     ('I',
		      'mask',
		      'Mask for not allowed player Ids (On bits are NOT allowed to be chosen)')],
		 4: [('I', 'objectid', "The object's Id number."), ('qqq', 'relpos', None)],
		 5: [('i', 'value', 'The Value'),
		     ('i', 'minvalue', 'The minimum value the value can take'),
		     ('i', 'maxvalue', 'The maximum value the value can take'),
		     ('i', 'increment', 'The amount to increment by (resolution)')],
		 6: [('[IsI]',
		      'possibleselections',
		      'A list of the items which can be chosen.'),
		     ('[II]', 'selection', 'A list of the items which have been selected.')],
		 7: [('I', 'maxlength', 'The maximum length of the string'),
		     ('s', 'string', None)],
		 8: [('I', 'reference', 'The generic reference to something.'),
		     ('[I]', 'allowed', 'A list of allowed valid reference types.')],
		 9: [('[I]', 'references', 'The list of references.'),
		     ('[I]', 'allowed', 'A list of allowed valid reference types.')],
		 10: [('[II]',
		       'allowed',
		       'The list of possible resources and allowable maximums.'),
		      ('I', 'maxmass', 'The maximum mass allowed.'),
		      ('I', 'maxvolument', 'The maximum volume allowed.'),
		      ('[II]',
		       'selected',
		       'The list of the selected Resources and quantities.')],
		 11: [('[I[iI]]',
		       'weightmaximums',
		       'Defines the maximums for the various weights.'),
		      ('[Isj[iI][I]]',
		       'possibles',
		       'This list defines the types of things that can be selected, weights and maximums.'),
		      ('[II]', 'selection', 'A list of the items which have been selected.')]}

OrderParamsStructDesc = \
		{}


ObjectParamsName = \
		{0: 'objectParamPosition3d',
		 1: 'objectParamVelocity3d',
		 2: 'objectParamAcceleration3d',
		 3: 'objectParamBoundPosition',
		 4: 'objectParamOrderQueue',
		 5: 'objectParamResourceList',
		 6: 'objectParmReference',
		 7: 'objectParamReferenceQuantityList',
		 8: 'objectParamInteger',
		 9: 'objectParamSize',
		 10: 'objectParamMedia'}

ObjectParamsDesc = \
		{0: 'A vector for the position.',
		 1: 'A vector for the velocity.',
		 2: 'A vector for the acceleration.',
		 3: "Object is bound to ('in') an Object.",
		 4: 'An order queue.',
		 5: 'A list of resources.',
		 6: 'A generic reference to something.',
		 7: 'Gives a list of references and how many of each of them.',
		 8: 'An Integer, informational.',
		 9: 'The diameter of the object.',
		 10: 'The url for the media for this object, either relative to the base url given in the Game frame, of absolute.'}

ObjectParamsStructUse = \
		{0: [('qqq', 'position', None),
		     ('I', 'relative', 'The object ID this position is relative to.')],
		 1: [('qqq', 'velocity', None),
		     ('I', 'relative', 'The object ID this vector is relative to.')],
		 2: [('qqq', 'vector', None),
		     ('I', 'relative', 'The object ID this vector is relative to.')],
		 3: [('i', 'slot', 'The slot in the parent object this object is in.')],
		 4: [('I', 'queueid', 'The ID number of the queue.'),
		     ('I', 'numorders', 'The number of orders in the queue.'),
		     ('[I]',
		      'ordertypes',
		      'A list of order types that can be put in this queue.')],
		 5: [('[IIII]', 'resources', 'A list of resources.')],
		 6: [('i', 'type', 'type of thing being referenced'), ('I', 'id', None)],
		 7: [('[iII]',
		      'references',
		      'A list of as described in the Generic Reference System')],
		 8: [('I', 'intvalue', 'The value of the integer parameter.')],
		 9: [('Q', 'size', 'The size of the object (diameter).')],
		 10: [('s', 'url', 'The url for the media.')]}

ObjectParamsStructDesc = \
		{4: [('I',
		      'maxslots',
		      'The maximum number of slots that can be used in this queue.')]}


