# LVarsetet Copyright (c) 2025 Luca Corti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




import debugpy
import FreeCAD, FreeCADGui
from PySide2 import QtWidgets, QtUiTools, QtCore#, QtGui
from PySide2.QtCore import QFile,Qt
from PySide2.QtUiTools import QUiLoader
import os


d=FreeCAD.ActiveDocument

NotAllowedObjects = ['ActiveView','AdditiveLoft','AdditivePipe','ArcFitTolerance',
'DocumentObjectGroup','DrawLeaderLine','DrawPage','DrawRichAnno','DrawSVGTemplate',
'DrawViewImage','DrawViewAnnotation','Line','Origin','Part','Plane','Sheet'
]

AllowedProperties = [
'Angle','Angle1','ActiveView','Angle2','Angle3','AttachmentOffset',
'Constraints','CustomThreadClearance','Depth','Diameter',
'DrillPointAngle','FirstAngle','Height','HoleCutCountersinkAngle','HoleCutDepth','HoleCutDiameter',
'Length','Length2','LengthFwd','LengthRev','Occurrences','Offset','Pad','Placement','Radius','Radius1','Radius2','Radius3',
'SecondAngle','Size','Size2','TaperAngle','TaperAngleRev','TaperAngle2','TaperedAngle','ThreadDepth',
'ThreadDiameter','ThreadDirection','Value','Width','x','y','z'
]

Unit =['mm','cm','m','in','ft','µm','nm','km','\°','deg','rad','gon','mm²',
'cm²','m²','in²','ft²','mm³','cm³','m³','in³','ft³']

''','kg','g','mg','lb','oz','kg/m³','g/cm³','lb/in³',
'N','lbf','Pa','kPa','MPa','bar','psi','J','kJ','MJ','Wh','kWh','W','kW','MW','hp',
'K','°C','°F','s','min','h','m/s','km/h','mm/s','ft/s','m/s²','mm/s²','ft/s²','N·m','lbf·ft','kgf·cm',
'kg·m²','kg·mm²'
]'''


#**************************************************
#*******  CREDITS AND CREATION OF LVarsets  *********
#**************************************************
if FreeCAD.ActiveDocument.getObject("LVarset"):
	LVarset=FreeCAD.ActiveDocument.getObject("LVarset")
else:
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(''''
******************************************************************
***************          LVarsetet 0.1-Beta         ******************
******************************************************************\n
Copyright (c) 2025 Luca Corti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License  Version 3
# This software uses PySide2 (Qt for Python)
#released under the LGPL v3 license and developed by The Qt Company.
#The user can obtain a copy of the library and its source code 
#by visiting: https://wiki.qt.io/Qt_for_Python 
#The source code of this software remains the property of the author.''')
	

	msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
	ret = msgBox.exec_()
	LVarset=App.activeDocument().addObject('App::VarSet','LVarset') # adds a varset named LVarset

#*********************** ************************************************
#***************     OBJECT DATA EXTRACTION      *******************
#***********************************************************************
# at the end Objects will contain all the permitted objects in the drawing
# that have at least one property still to be inserted in the LVarset Objects
Object=[]
Objects=[]
NOgg=len(FreeCAD.ActiveDocument.Objects)
Counter =0

for x in range(NOgg): # cycle through all objects
	XObject=d.Objects[x]
	if XObject.TypeId.split("::")[1] in NotAllowedObjects:
		continue # if it is a not allowed object, ignore it
	for i in range(len(XObject.PropertiesList)): # cycle through all properties of that object
		Property = XObject.PropertiesList[i]
		if  not Property in AllowedProperties: 
			continue
		if 'ReadOnly' in XObject.getPropertyStatus(XObject.PropertiesList[i]):
			continue #cannot be modified, skip to next
		if  Property == "AttachmentOffset" :# if the property is an AttOff
			if not f"{XObject.Name}AttOff" in LVarset.PropertiesList:
				Object.append(["AttOff", XObject.AttachmentOffset.Matrix, 0])
				Counter += 1
				continue
		elif  Property == "Placement" :# if the property is an Placement

			if not f"{XObject.Name}PlacementPosX" in LVarset.PropertiesList:
			## if there is NO Property with that name in the LVarset
				Object.append([f"{XObject.Name}Placement", XObject.Placement.Base, 0])
				Counter += 1
				continue
			# if the property is neither a constraint nor an AttOff

		elif  Property == 'Constraints' : # if the property is a constraint
			for ii in  range(XObject.ConstraintCount):
				try: XObject.getDatum(ii) # check if it's modifiable data or, for example, CostraintCoincident
				except:
					continue # It is a constraint but not modifiable, e.g., ConstraintCoincident. Move on to the next property.
				try: XObject.Constraints[ii].Driven
				except:
					pass # okproperty modifiable
				else:
					continue # it's a constraint, it's writable data, but it's blocked, move on to another property
				Data=str(XObject.getDatum(ii))
				x=Data.find(" ")
				Data=Data[:x]# removes space and unit
				if XObject.Constraints[ii].Name:
					if not f"{XObject.Name}{XObject.Constraints[ii].Name}" in LVarset.PropertiesList:
						Object.append([f"{XObject.Constraints[ii].Name}",Data,0])# no property, adding to object
						Counter +=1 # a Property has been added
				elif not f"{XObject.Name}{XObject.Constraints[ii]}" in LVarset.PropertiesList:
					Object.append([f"Constraint{ii+1}",Data,0]) # no alias add to object
					Counter +=1
		else:
			if not f"{XObject.Name}{Property}" in LVarset.PropertiesList:
					Dato=str(getattr(XObject,Property)) # se Alias NON e' gia' presente nel foglio
					x=Dato.find(" ")
					if x>0:
						Dato=Dato[:x]# toglie spazio e unita'
					Object.append([Property,Dato,0])
					Counter +=1
	if Counter: #if any Properties have been added to Object
		Object.insert(0,["Name",XObject.Name,0])
		Object.insert(0,["Label",XObject.Label.replace("-","").replace("+","").replace(".",""),0])
		Counter=0# add Data=‘’
		Objects.append(Object)
	Object=[]
	Counter =0
print("creation of Objects ok\n")

#***********************************************
#********  CLASS Window1   ********
#***********************************************

class Window1(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		base_path = os.path.dirname(__file__)
		ui_path = os.path.join(base_path, "LVarset.ui")
		ui_file = QFile(ui_path)
		if not ui_file.exists():
			return
		ui_file.open(QFile.ReadOnly)
		loader = QtUiTools.QUiLoader()
		self.ui = loader.load(ui_file, self)		
		self.ui.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		layout = QtWidgets.QVBoxLayout(self)
		layout.addWidget(self.ui)
		layout.setContentsMargins(10,10,10,10)
		layout.setSpacing(0)
		ui_file.close()
		
		self.XOggetti=[]
		self.NOgg=0
#++++++++++++++++    WIDGET   +++++++++++++++++++++++++++++++++++
		self.OBjectsLabel = self.ui.findChild(QtWidgets.QLabel, "OBjectsLabel")
		self.ObjComb = self.ui.findChild(QtWidgets.QComboBox, "ObjCombo")
		self.DeSelAl= self.ui.findChild(QtWidgets.QPushButton, "DeSelAll")
		self.SelAl = self.ui.findChild(QtWidgets.QPushButton, "SelAll")
		self.PropertiesLabel = self.ui.findChild(QtWidgets.QLabel, "PropertiesLabel")
		self.ListProperties = self.ui.findChild(QtWidgets.QListWidget, "ListProperties")
		self.CompileVar = self.ui.findChild(QtWidgets.QPushButton, "CompileVars")
		self.Exi = self.ui.findChild(QtWidgets.QPushButton, "Exit")
		
#+++++++++++++++    EVENTI    +++++++++++++++++++++++++++++++++++++
		self.DeSelAl.clicked.connect(self.DeselectAll)# 
		self.SelAl.clicked.connect(self.SelectAll)
		self.Exi.clicked.connect(self.Exit)
		self.CompileVar.clicked.connect(self.CompileVars)
		self.ObjComb.currentIndexChanged.connect(lambda: self.UpdatePropList())
		self.FillForm()
		
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++		
#++++++++++++++    METHODS    +++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#******************   FillForm   +++++++++++++++++++++++++++++++
#****************************************************************
# fills the ComboBox with the names of all Objects in Object 
# and the list with all the properties of the first Object of Objects
# sets self.NOgg to 0 (first Object in the list)
	def FillForm(self):

#******************   Fills ComboBox   ++++++++++++++++++++++++++
		for Object in Objects:
			self.ObjComb.addItem(f"{Object[0][1]}--{Object[1][1]}\n")
			self.NOgg=0
#******************   Fill QListWidget   ++++++++++++++++++++++++++
		XObject= Objects[self.NOgg]
		self.ListProperties.clear()
		for x,y,z in XObject[2:]: #Property starting from the third (excluding Name and Label
			xitem = QtWidgets.QListWidgetItem(str(f"{x}".ljust(13," ") + f" = {y}"))
			self.ListProperties.addItem(xitem)
			xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
			xitem.setCheckState(Qt.Unchecked)

#+++++++++++    DeSelTutto    ++++++++++++++++++++++++++
#****************************************************************
	def DeselectAll(self):
		for i in range(self.ListProperties.count()):
			item = self.ListProperties.item(i)
			item.setCheckState(Qt.Unchecked)
	
#+++++++++++    SelectAll    ++++++++++++++++++++++++++
#****************************************************************
	def SelectAll(self):
		for i in range(self.ListProperties.count()):
			item = self.ListProperties.item(i)
			item.setCheckState(Qt.Checked)
	
#+++++++++++    Exit    ++++++++++++++++++++++++++
#****************************************************************
	def Exit(self):
		self.close()
		self.deleteLater()

#+++++++++++    UpdatePropList    ++++++++++++++++++++++++++
#****************************************************************
# cycles through the Properties of XObject in the list and if they are checked,
# checks them to 1 in Objects, then clears the list and repopulates it
#  with the Properties of the current Object in the ComboBox 
	def UpdatePropList(self):
		# self.NOgg is the index of the previous object
		for i in range(self.ListProperties.count()):
			item = self.ListProperties.item(i)
			if item.checkState() == Qt.Checked:
				Objects[self.NOgg][i+2] [2]=1# flags the Property' of Objects
			else:
				pass
# ***** clears and writes the properties of the current Object ++++‘’'
		self.ListProperties.clear()
		self.NOgg= self.ObjComb.currentIndex()#remember the current object
		for x,y,z in Objects[self.NOgg][2:]: #Property starting from the third (excluding Name and Label
			if z==0:
				xitem = QtWidgets.QListWidgetItem(str(f"{x}".ljust(30," ") + f" = {y}"))
				self.ListProperties.addItem(xitem)
				xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
				xitem.setCheckState(Qt.Unchecked)
			elif z==1:
				xitem = QtWidgets.QListWidgetItem(str(f"{x}".ljust(30," ") + f" = {y}"))
				self.ListProperties.addItem(xitem)
				xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
				xitem.setCheckState(Qt.Checked)
			else:
				print("******  ERROR   ******\n")
				pass
			d.recompute()
	a=3
	d.recompute()
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#***************      LVarset     ***************************
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def CompileVars(self):

		self.UpdatePropList()
		debugpy.breakpoint()

		c=0
		for XObject in reversed(Objects):# cycles from last to first, so when an object is deleted, the sequence is broken
			GroupName=XObject[0][1].replace("-","").replace("+","").replace(".","")
			x=0 #to check if there are any Properties left to import
			for Property in XObject[2:]: # e.g. [‘Height’, ‘10.0 ’, 0]
				if Property[2]==1: # =flagged

#**********************************************************************************				
#**********            writes Property, in the Varset          ********************
#**********************************************************************************

					if "AttOff" in Property[0] :    # Check if it is an AttachmentOffset
						Angle = d.getObject(XObject[1][1]).AttachmentOffset.Rotation.Angle*180/3.141592653589793
						LVarset.addProperty('App::PropertyAngle', f'{XObject[1][1]}AttOffAngle' , GroupName)
						setattr(LVarset, f'{XObject[1][1]}AttOffAngle',Angle)

						PosX= d.getObject(XObject[1][1]).AttachmentOffset.Base.x
						PosY= d.getObject(XObject[1][1]).AttachmentOffset.Base.y
						PosZ= d.getObject(XObject[1][1]).AttachmentOffset.Base.z

						for i,ii in ((PosX,f'{XObject[1][1]}AttOffPosX'),(PosY,f'{XObject[1][1]}AttOffPosY'),(PosZ,f'{XObject[1][1]}AttOffPosZ')):
							PropertyName=ii
							LVarset.addProperty('App::PropertyFloat', PropertyName , GroupName)
							setattr(LVarset, PropertyName , i)
						c+=1

					elif "Placement" in Property[0] :    # Check if it is a Placement
						Angle = d.getObject(XObject[1][1]).Placement.Rotation.Angle*180/3.141592653589793
						LVarset.addProperty('App::PropertyAngle', f'{XObject[1][1]}PlacementAngle' , GroupName)
						setattr(LVarset, f'{XObject[1][1]}PlacementAngle',Angle)

						PosX= d.getObject(XObject[1][1]).Placement.Base.x
						PosY= d.getObject(XObject[1][1]).Placement.Base.y
						PosZ= d.getObject(XObject[1][1]).Placement.Base.z
						for i,ii in ((PosX,f'{XObject[1][1]}PlacementPosX'),(PosY,f'{XObject[1][1]}PlacementPosY'),(PosZ,f'{XObject[1][1]}PlacementPosZ')):
							PropertyName=ii
							LVarset.addProperty('App::PropertyFloat', PropertyName , GroupName)
							setattr(LVarset, PropertyName , i)
						c+=1
					else:# Others
						PropertyName=f'{XObject[1][1]}{Property[0]}'
						LVarset.addProperty('App::PropertyFloat', PropertyName , GroupName)
						setattr(LVarset, PropertyName, float(Property[1]))
						c+=1
					d.recompute()
#************************************************************************************************					
#*****************                    writes Formula in Object            ***********************
#************************************************************************************************					

					ogg= d.getObject(XObject[1][1])#e.g. ‘Sketch001’
					if "AttOff" in Property[0] :    # Check if it is an AttachmentOffset

						for i,ii in (('AttachmentOffset.Rotation.Angle',f'LVarset.{XObject[1][1]}AttOffAngle'),('AttachmentOffset.Base.x',f'LVarset.{XObject[1][1]}AttOffPosX'),('AttachmentOffset.Base.y',f'LVarset.{XObject[1][1]}AttOffPosY'),('AttachmentOffset.Base.z',f'LVarset.{XObject[1][1]}AttOffPosZ')):
							ogg.setExpression(i,ii)
							b=0

					elif "Placement" in Property[0] :    # Check if it is an Placement

						for i,ii in (('Placement.Rotation.Angle',f'LVarset.{XObject[1][1]}PlacementAngle'),('Placement.Base.x',f'LVarset.{XObject[1][1]}PlacementPosX'),('Placement.Base.y',f'LVarset.{XObject[1][1]}PlacementPosY'),('Placement.Base.z',f'LVarset.{XObject[1][1]}PlacementPosZ')):
							ogg.setExpression(i,ii)#+++es. Placement.Rotation.Angle , LVarset.SketchPlacementAngle
							b=0

					else:
						try:     #check if it is a modifiable constraint
							ogg.getDatum(Property[0])
							if "Constraint" in Property[0] :    #e.g. ‘Constraint6’ try to see if the constraint does not have a name
								aa=f"Constraints[{int(Property[0][10:])-1}]"
								Expression=f'LVarset.{XObject[1][1]}{Property[0]}' #+++es. 
								ogg.setExpression(aa,Expression) # e.g. <Sketcher::SketchObject>.setExpression(Constraint[6], ‘LVarset.         Sketch_Constraint6’)
							else:     # if there isn't Constraintin the name then it's a constraint with a name' like es. 'BoxLenght'
								aa=f"Constraints[{ogg.getIndexByName(Property[0])}]"
								Expression=f'LVarset.{XObject[1][1]}{Property[0]}' #+++es. 
								ogg.setExpression(aa,Expression)
						except Exception as e:     # if it is not a Constraint(Datum) then it is a Property' type e.g. Value or Occurrence
							Expression=f'LVarset.{XObject[1][1]}{Property[0]}' #+++es. 
							ogg.setExpression(Property[0],Expression)# es. <Sketcher::SketchObject>.setExpression(Largh, 'LVarset.Sketch_Largh')

					#******     removes the Property from Objects so that it is no longer listed   ********
					Objects[Objects.index(XObject)].remove(Property)
				else:
					#*******    otherwise remember not to delete the entire XObject
					x =1
			d.recompute()
			if x== 0:
#******         If there are no more Properties, remove XObject from Objects   ********
				Objects.remove(XObject)
			c=3
		#self.NObject=0
		d.recompute()
		#self.ListProperties.clear()
		XObject=[]
		self.XObjects=[]



		self.ListProperties.clear()
		self.ObjComb.clear()
		self.NOgg=-1
		self.FillForm()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


Window1 = Window1()
screen = Window1.screen().availableGeometry()
x = screen.x() + (screen.width() - Window1.width()) // 3
y = screen.y() + (screen.height() - Window1.height()) // 5
Window1.move(x, y)
Window1.show()

#++++++++++++        END     +++++++++++++++++++++++++++++++++++++++++
