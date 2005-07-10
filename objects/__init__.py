# Mapping to store between type numbers and classes
mapping = {}

# Constants
import constants
constants = constants

# Header
from objects.Header import Header, Processed, SetVersion, GetVersion
Header = Header
Header.mapping = mapping

Processed = Processed
SetVersion = SetVersion
GetVersion = GetVersion

# Special Description Stuff
from objects.Description import DescriptionError, Describable, Description
DescriptionError = DescriptionError
Describable = Describable
Description = Description

# Base
from objects.Base import GetWithID
GetWithID = GetWithID

from objects.Base import GetWithIDandSlot
GetWithIDandSlot = GetWithIDandSlot

from objects.Base import GetIDSequence
GetIDSequence = GetIDSequence

from objects.Base import IDSequence
IDSequence = IDSequence

# Generic Responses
from objects.OK import OK
OK = OK
mapping[OK.no] = OK

from objects.Fail import Fail
Fail = Fail
mapping[Fail.no] = Fail

from objects.Sequence import Sequence
Sequence = Sequence
mapping[Sequence.no] = Sequence

# Connecting
from objects.Connect import Connect
Connect = Connect
mapping[Connect.no] = Connect

from objects.Login import Login
Login = Login
mapping[Login.no] = Login

from objects.Ping import Ping
Ping = Ping
mapping[Ping.no] = Ping

# Features
from objects.Feature_Get import Feature_Get
Feature_Get = Feature_Get
mapping[Feature_Get.no] = Feature_Get

from objects.Feature import Feature
Feature = Feature
mapping[Feature.no] = Feature

# Objects
from objects.Object_GetById import Object_GetById
Object_GetById = Object_GetById
mapping[Object_GetById.no] = Object_GetById

from objects.Object import Object
Object = Object
mapping[Object.no] = Object

from objects.Object_GetID import Object_GetID
Object_GetID = Object_GetID
mapping[Object_GetID.no] = Object_GetID

from objects.Object_GetID_ByPos import Object_GetID_ByPos
Object_GetID_ByPos = Object_GetID_ByPos
mapping[Object_GetID_ByPos.no] = Object_GetID_ByPos

from objects.Object_GetID_ByContainer import Object_GetID_ByContainer
Object_GetID_ByContainer = Object_GetID_ByContainer
mapping[Object_GetID_ByContainer.no] = Object_GetID_ByContainer

from objects.Object_IDSequence import Object_IDSequence
Object_IDSequence = Object_IDSequence
mapping[Object_IDSequence.no] = Object_IDSequence

from objects.ObjectDesc import descriptions
ObjectDescs = descriptions

# Orders
from objects.OrderDesc_Get import OrderDesc_Get
OrderDesc_Get = OrderDesc_Get
mapping[OrderDesc_Get.no] = OrderDesc_Get

from objects.OrderDesc import OrderDesc, descriptions
OrderDesc = OrderDesc
OrderDescs = descriptions
mapping[OrderDesc.no] = OrderDesc

from objects.OrderDesc_GetID import OrderDesc_GetID
OrderDesc_GetID = OrderDesc_GetID
mapping[OrderDesc_GetID] = OrderDesc_GetID

from objects.OrderDesc_IDSequence import OrderDesc_IDSequence
OrderDesc_IDSequence = OrderDesc_IDSequence
mapping[OrderDesc_IDSequence] = OrderDesc_IDSequence

from objects.Order_Get import Order_Get
Order_Get = Order_Get
mapping[Order_Get.no] = Order_Get

from objects.Order import Order
Order = Order
mapping[Order.no] = Order

from objects.Order_Insert import Order_Insert
Order_Insert = Order_Insert
mapping[Order_Insert.no] = Order_Insert

from objects.Order_Remove import Order_Remove
Order_Remove = Order_Remove
mapping[Order_Remove.no] = Order_Remove

from objects.Order_Probe import Order_Probe
Order_Probe = Order_Probe
mapping[Order_Probe.no] = Order_Probe

# Time
from objects.TimeRemaining_Get import TimeRemaining_Get
TimeRemaining_Get = TimeRemaining_Get
mapping[TimeRemaining_Get.no] = TimeRemaining_Get

from objects.TimeRemaining import TimeRemaining
TimeRemaining = TimeRemaining
mapping[TimeRemaining.no] = TimeRemaining

# Messages

from objects.Board_Get import Board_Get
Board_Get = Board_Get
mapping[Board_Get.no] = Board_Get

from objects.Board import Board
Board = Board
mapping[Board.no] = Board

from objects.Board_GetID import Board_GetID
Board_GetID = Board_GetID
mapping[Board_GetID.no] = Board_GetID

from objects.Board_IDSequence import Board_IDSequence
Board_IDSequence = Board_IDSequence
mapping[Board_IDSequence.no] = Board_IDSequence

from objects.Message_Get import Message_Get
Message_Get = Message_Get
mapping[Message_Get.no] = Message_Get

from objects.Message import Message
Message = Message
mapping[Message.no] = Message

from objects.Message_Insert import Message_Insert
Message_Insert = Message_Insert
mapping[Message_Insert.no] = Message_Insert

from objects.Message_Remove import Message_Remove
Message_Remove = Message_Remove
mapping[Message_Remove.no] = Message_Remove

# Resource Stuff
from objects.Resource_Get import Resource_Get
Resource_Get = Resource_Get
mapping[Resource_Get.no] = Resource_Get

from objects.Resource import Resource
Resource = Resource
mapping[Resource.no] = Resource

from objects.Resource_GetID import Resource_GetID
Resource_GetID = Resource_GetID
mapping[Resource_GetID.no] = Resource_GetID

from objects.Resource_IDSequence import Resource_IDSequence
Resource_IDSequence = Resource_IDSequence
mapping[Resource_IDSequence.no] = Resource_IDSequence

# Design Categories
from objects.Category_Get import Category_Get
Category_Get = Category_Get
mapping[Category_Get.no] = Category_Get

from objects.Category import Category
Category = Category
mapping[Category.no] = Category

from objects.Category_Add import Category_Add
Category_Add = Category_Add
mapping[Category_Add.no] = Category_Add

from objects.Category_Remove import Category_Remove
Category_Remove = Category_Remove
mapping[Category_Remove.no] = Category_Remove

from objects.Category_GetID import Category_GetID
Category_GetID = Category_GetID
mapping[Category_GetID.no] = Category_GetID

from objects.Category_IDSequence import Category_IDSequence
Category_IDSequence = Category_IDSequence
mapping[Category_IDSequence.no] = Category_IDSequence

# Design Designs
from objects.Design_Get import Design_Get
Design_Get = Design_Get
mapping[Design_Get.no] = Design_Get

from objects.Design import Design
Design = Design
mapping[Design.no] = Design

from objects.Design_Add import Design_Add
Design_Add = Design_Add
mapping[Design_Add.no] = Design_Add

from objects.Design_Remove import Design_Remove
Design_Remove = Design_Remove
mapping[Design_Remove.no] = Design_Remove

from objects.Design_GetID import Design_GetID
Design_GetID = Design_GetID
mapping[Design_GetID.no] = Design_GetID

from objects.Design_IDSequence import Design_IDSequence
Design_IDSequence = Design_IDSequence
mapping[Design_IDSequence.no] = Design_IDSequence

# Design Components
from objects.Component_Get import Component_Get
Component_Get = Component_Get
mapping[Component_Get.no] = Component_Get

from objects.Component import Component
Component = Component
mapping[Component.no] = Component

from objects.Component import Component
Component = Component
mapping[Component.no] = Component

from objects.Component_GetID import Component_GetID
Component_GetID = Component_GetID
mapping[Component_GetID.no] = Component_GetID

from objects.Component_IDSequence import Component_IDSequence
Component_IDSequence = Component_IDSequence
mapping[Component_IDSequence.no] = Component_IDSequence

# Design Properties
from objects.Property_Get import Property_Get
Property_Get = Property_Get
mapping[Property_Get.no] = Property_Get

from objects.Property import Property
Property = Property
mapping[Property.no] = Property

from objects.Property import Property
Property = Property
mapping[Property.no] = Property

from objects.Property_GetID import Property_GetID
Property_GetID = Property_GetID
mapping[Property_GetID.no] = Property_GetID

from objects.Property_IDSequence import Property_IDSequence
Property_IDSequence = Property_IDSequence
mapping[Property_IDSequence.no] = Property_IDSequence

