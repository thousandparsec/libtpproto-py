# Mapping to store between type numbers and classes
mapping = {}

from Header import Header, Processed
Header = Header
Header.mapping = mapping

Processed = Processed

# Generic Responses
from OK import OK
OK = OK
mapping[OK.no] = OK

from Fail import Fail
Fail = Fail
mapping[Fail.no] = Fail

from Sequence import Sequence
Sequence = Sequence
mapping[Sequence.no] = Sequence

# Connecting
from Connect import Connect
Connect = Connect
mapping[Connect.no] = Connect

from Login import Login
Login = Login
mapping[Login.no] = Login

# Objects
from Object_GetById import Object_GetById
Object_GetById = Object_GetById
mapping[Object_GetById.no] = Object_GetById

from Object_GetByPos import Object_GetByPos
Object_GetByPos = Object_GetByPos
mapping[Object_GetByPos.no] = Object_GetByPos

from Object import Object
Object = Object
mapping[Object.no] = Object

## Orders
#from OrderDesc_Get import OrderDesc_Get
#OrderDesc_Get = OrderDesc_Get
#mapping[OrderDesc_Get.no] = OrderDesc_Get
#
#from OrderDesc import OrderDesc
#OrderDesc = OrderDesc
#mapping[OrderDesc.no] = OrderDesc

from Order_Get import Order_Get
Order_Get = Order_Get
mapping[Order_Get.no] = Order_Get

#from Order import Order
#Order = Order
#mapping[Order.no] = Order
#
#from Order_Add import Order_Add
#Order_Add = Order_Add
#mapping[Order_Add.no] = Order_Add

from Order_Remove import Order_Remove
Order_Remove = Order_Remove
mapping[Order_Remove.no] = Order_Remove

## Time
#
## Message
#from Board_Get import Board_Get
#Board_Get = Board_Get
#mapping[Board_Get.no] = Board_Get
#
#from Board import Board
#Board = Board
#mapping[Board.no] = Board
#
#from Message_Get import Message_Get
#Message_Get = Message_Get
#mapping[Message_Get.no] = Message_Get
#
#from Message import Message
#Message = Message
#mapping[Message.no] = Message
#
#from Message_Post import Message_Post
#Message_Post = Message_Post
#mapping[Message_Post.no] = Message_Post
#
