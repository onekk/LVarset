# LVarsetet_0_1_Beta Copyright (c) 2025 Luca Corti
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

from pathlib import Path
from math import pi

import FreeCAD
# import FreeCADGui

from PySide import QtCore, QtWidgets, QtUiTools

QUiLoader = QtUiTools.QUiLoader
QFile = QtCore.QFile
Qt = QtCore.Qt


if FreeCAD.ActiveDocument is None:
    QtWidgets.QMessageBox.critical(
        None, "LVarset",
        "No active document.\nPlease open or create a document first.")

d = FreeCAD.ActiveDocument


NotAllowedObjects = [
    'ActiveView', 'AdditiveLoft', 'AdditivePipe', 'ArcFitTolerance',
    'DocumentObjectGroup', 'DrawLeaderLine', 'DrawPage', 'DrawRichAnno',
    'DrawSVGTemplate', 'DrawViewImage', 'DrawViewAnnotation', 'Line', 'Origin',
    'Part', 'Plane', 'Sheet'
]

AllowedProperties = [
    'Angle', 'Angle1', 'ActiveView', 'Angle2', 'Angle3', 'AttachmentOffset',
    'Constraints', 'CustomThreadClearance', 'Depth', 'Diameter',
    'DrillPointAngle', 'FirstAngle', 'Height', 'HoleCutCountersinkAngle',
    'HoleCutDepth', 'HoleCutDiameter', 'Length', 'Length2', 'LengthFwd',
    'LengthRev', 'Occurrences', 'Offset', 'Pad', 'Placement', 'Radius',
    'Radius1', 'Radius2', 'Radius3', 'SecondAngle', 'Size', 'Size2',
    'TaperAngle', 'TaperAngleRev', 'TaperAngle2', 'TaperedAngle',
    'ThreadDepth', 'ThreadDiameter', 'ThreadDirection', 'Value', 'Width',
    'x', 'y', 'z'
]


# **************************************************
# *******  CREDITS AND CREATION OF LVarsets  *******
# **************************************************

if FreeCAD.ActiveDocument.getObject("LVarset"):
    LVarset = FreeCAD.ActiveDocument.getObject("LVarset")
else:
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(''''
**************************************************************************
***************          LVarset_0.1_Beta         ************************
**************************************************************************
#                   Copyright (c) 2025 Luca Corti
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# Version 3
# released under the LGPL v3 license and developed by The
# Qt Company.
# This program is a BETA version, and is distributed
#       WITHOUT ANY WARRANTY.
# The source code of this software remains
# the property of the author.''')

    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    ret = msgBox.exec()
    LVarset = FreeCAD.ActiveDocument.addObject('App::VarSet', 'LVarset')


# ------------------------------------------------
#              OBJECT DATA EXTRACTION
# ------------------------------------------------
# at the end Objects will contain all the permitted objects in the drawing
# that have at least one property still to be inserted in the LVarset Objects

Object = []
Objects = []
NOgg = len(FreeCAD.ActiveDocument.Objects)
Counter = 0

for x in range(NOgg):  # cycle through all objects
    XObject = d.Objects[x]
    type_name = XObject.TypeId.split("::")[-1]
    if type_name in NotAllowedObjects:
        continue  # if it is a not allowed object, ignore it

    for i in range(len(XObject.PropertiesList)):
        # cycle through all properties of that object
        Property = XObject.PropertiesList[i]
        if Property not in AllowedProperties:
            continue
        if 'ReadOnly' in XObject.getPropertyStatus(XObject.PropertiesList[i]):
            continue  # cannot be modified, skip to next
        if Property == "AttachmentOffset":  # if the property is an AttOff
            if not f"{XObject.Name}AttOff" in LVarset.PropertiesList:
                Object.append(["AttOff", XObject.AttachmentOffset.Matrix, 0])
                Counter += 1
                continue
        elif Property == "Placement":  # if the property is an Placement

            if not f"{XObject.Name}PlacementPosX" in LVarset.PropertiesList:
                # if there is NO Property with that name in the LVarset
                Object.append(
                    [f"{XObject.Name}Placement", XObject.Placement.Base, 0])
                Counter += 1
                continue
            # if the property is neither a constraint nor an AttOff

        elif Property == 'Constraints':  # if the property is a constraint
            for ii in range(XObject.ConstraintCount):
                try:
                    # check if it's modifiable data or, for example,
                    # ConstraintCoincident
                    XObject.getDatum(ii)
                except:
                    # It is a constraint but not modifiable, e.g.
                    # ConstraintCoincident. Move on to the next property.
                    continue
                try:
                    XObject.Constraints[ii].Driven
                except:
                    # ok property modifiable
                    pass
                else:
                    # it's a constraint, it's writable data, but it's blocked,
                    # move on to another property
                    continue
                Data = str(XObject.getDatum(ii))
                x = Data.find(" ")
                Data = Data[:x]  # removes space and unit
                if XObject.Constraints[ii].Name:
                    if f"{XObject.Name}{XObject.Constraints[ii].Name}" not in LVarset.PropertiesList:
                        # no property, adding to object
                        Object.append([f"{XObject.Constraints[ii].Name}", Data, 0])
                        Counter += 1  # a Property has been added
                elif f"{XObject.Name}{XObject.Constraints[ii]}" not in LVarset.PropertiesList:
                    # non in varset add to object
                    Object.append([f"Constraint{ii+1}", Data, 0])
                    Counter += 1
        else:
            if f"{XObject.Name}{Property}" not in LVarset.PropertiesList:
                # if Property is not already in VarSet
                Data = str(getattr(XObject, Property))
                x = Data.find(" ")
                if x > 0:
                    Data = Data[:x]  # delete space and Unit
                    Object.append([Property, Data, 0])
                    Counter += 1
    if Counter:  # if any Properties have been added to Object
        Object.insert(0, ["Name", XObject.Name, 0])
        Object.insert(
            0,
            ["Label",
             XObject.Label.replace("-", "").replace("+", "").replace(".", ""),
             0])
        Counter = 0  # add Data=‘’
        Objects.append(Object)
    Object = []
    Counter = 0

print("creation of Objects ok\n")


# ------------------------------------------------
#                   CLASS Window1
# ------------------------------------------------


class Window1(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).parent / "LVarset.ui"

        if not ui_path.exists():
            raise FileNotFoundError(f"UI file not found: {ui_path}")
        ui_file = QtCore.QFile(str(ui_path))

        if not ui_file.open(QtCore.QFile.ReadOnly):
            raise RuntimeError("Cannot open UI file")

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError("Failed to load UI file")

        self.ui.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self.XOggetti = []
        self.NOgg = 0

        # ----------------------------------------
        #                  WIDGET
        # ----------------------------------------

        # se Property NON e' gia' presente nel varset
        self.OBjectsLabel = self.ui.findChild(QtWidgets.QLabel, "OBjectsLabel")
        self.ObjComb = self.ui.findChild(QtWidgets.QComboBox, "ObjCombo")
        self.DeSelAl = self.ui.findChild(QtWidgets.QPushButton, "DeSelAll")
        self.SelAl = self.ui.findChild(QtWidgets.QPushButton, "SelAll")
        self.PropertiesLabel = self.ui.findChild(QtWidgets.QLabel, "PropertiesLabel")
        self.ListProperties = self.ui.findChild(QtWidgets.QListWidget, "ListProperties")
        self.CompileVar = self.ui.findChild(QtWidgets.QPushButton, "CompileVars")
        self.Exi = self.ui.findChild(QtWidgets.QPushButton, "Exit")

        # ----------------------------------------
        #                  EVENTS
        # ----------------------------------------

        self.DeSelAl.clicked.connect(self.DeselectAll)
        self.SelAl.clicked.connect(self.SelectAll)
        self.Exi.clicked.connect(self.Exit)
        self.CompileVar.clicked.connect(self.CompileVars)
        self.ObjComb.currentIndexChanged.connect(lambda: self.UpdatePropList())
        self.FillForm()

    # --------------------------------------------
    #                    METHODS
    # --------------------------------------------

    def FillForm(self):
        """Fills the ComboBox with the names of all Objects in Object
         and the list with all the properties of the first Object of Objects.

         sets self.NOgg to 0 (first Object in the list)"""

        # Fill ComboBox
        for Object in Objects:
            self.ObjComb.addItem(f"{Object[0][1]}--{Object[1][1]}")
            self.NOgg = 0

        # Fill QListWidget
        XObject = Objects[self.NOgg]
        self.ListProperties.clear()
        for x, y, z in XObject[2:]:
            # Property starting from the third (excluding Name and Label)
            xitem = QtWidgets.QListWidgetItem(
                str(f"{x}".ljust(13, " ") + f" = {y}"))
            self.ListProperties.addItem(xitem)
            xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
            xitem.setCheckState(Qt.Unchecked)

    def DeselectAll(self):
        for i in range(self.ListProperties.count()):
            item = self.ListProperties.item(i)
            item.setCheckState(Qt.Unchecked)

    def SelectAll(self):
        for i in range(self.ListProperties.count()):
            item = self.ListProperties.item(i)
            item.setCheckState(Qt.Checked)

    def Exit(self):
        self.close()
        self.deleteLater()

    def UpdatePropList(self):
        """Cycles through the Properties of XObject in the list and if they are
        checked, checks them to 1 in Objects, then clears the list and
        repopulates it with Properties of the current Object in the ComboBox
        """

        # self.NOgg is the index of the previous object
        for i in range(self.ListProperties.count()):
            item = self.ListProperties.item(i)
            if item.checkState() == Qt.Checked:
                Objects[self.NOgg][i+2][2] = 1  # flags the Property' of Objects
            else:
                pass
        # clears and writes the properties of the current Object
        self.ListProperties.clear()
        self.NOgg = self.ObjComb.currentIndex()  # remember the current object

        for x, y, z in Objects[self.NOgg][2:]:
            # Property starting from the third (excluding Name and Label
            if z == 0:
                xitem = QtWidgets.QListWidgetItem(
                    str(f"{x}".ljust(30, " ") + f" = {y}"))
                self.ListProperties.addItem(xitem)
                xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
                xitem.setCheckState(Qt.Unchecked)
            elif z == 1:
                xitem = QtWidgets.QListWidgetItem(
                    str(f"{x}".ljust(30, " ") + f" = {y}"))
                self.ListProperties.addItem(xitem)
                xitem.setFlags(xitem.flags() | QtCore.Qt.ItemIsUserCheckable)
                xitem.setCheckState(Qt.Checked)
            else:
                print("******  ERROR   ******\n")
                pass

    a = 3
    d.recompute()

    # --------------------------------------------
    #                    LVarset
    # --------------------------------------------

    def CompileVars(self):
        self.UpdatePropList()
        c = 0
        for XObject in reversed(Objects):
            GroupName = XObject[0][1].replace("-", "").replace("+", "").replace(".", "")
            x = 0  # to check if there are any Properties left to import
            for Property in XObject[2:]:  # e.g. [‘Height’, ‘10.0 ’, 0]
                if Property[2] == 1:  # = flagged
                    # writes Property, in the Varset

                    if "AttOff" in Property[0]:
                        # Check if it is an AttachmentOffset
                        obj11af = d.getObject(XObject[1][1]).AttachmentOffset
                        Angle = obj11af.Rotation.Angle * 180 / pi
                        LVarset.addProperty(
                            'App::PropertyAngle', f'{XObject[1][1]}AttOffAngle',
                            GroupName)
                        setattr(LVarset, f'{XObject[1][1]}AttOffAngle', Angle)

                        PosX = obj11af.Base.x
                        PosY = obj11af.Base.y
                        PosZ = obj11af.Base.z

                        for i, ii in (
                                (PosX, f'{XObject[1][1]}AttOffPosX'),
                                (PosY, f'{XObject[1][1]}AttOffPosY'),
                                (PosZ, f'{XObject[1][1]}AttOffPosZ')):
                            PropertyName = ii
                            LVarset.addProperty(
                                'App::PropertyFloat', PropertyName, GroupName)
                            setattr(LVarset, PropertyName, i)
                        c += 1

                    elif "Placement" in Property[0]: # Check if it is a Placement
                        obj11pl = d.getObject(XObject[1][1]).Placement
                        Angle = obj11pl.Rotation.Angle * 180 / pi
                        LVarset.addProperty(
                            'App::PropertyAngle', f'{XObject[1][1]}PlacementAngle',
                            GroupName)
                        setattr(LVarset, f'{XObject[1][1]}PlacementAngle', Angle)

                        PosX = obj11pl.Base.x
                        PosY = obj11pl.Base.y
                        PosZ = obj11pl.Base.z

                        for i, ii in (
                                (PosX, f'{XObject[1][1]}PlacementPosX'),
                                (PosY, f'{XObject[1][1]}PlacementPosY'),
                                (PosZ, f'{XObject[1][1]}PlacementPosZ')):
                            PropertyName = ii
                            LVarset.addProperty(
                                'App::PropertyFloat', PropertyName , GroupName)
                            setattr(LVarset, PropertyName, i)
                        c += 1
                    else:  # Others
                        PropertyName = f'{XObject[1][1]}{Property[0]}'
                        LVarset.addProperty(
                            'App::PropertyFloat', PropertyName, GroupName)
                        setattr(LVarset, PropertyName, float(Property[1]))
                        c += 1

                    # writes Formula in Object

                    ogg = d.getObject(XObject[1][1])  # e.g. ‘Sketch001’
                    if "AttOff" in Property[0]:  # Check if it is an AttachmentOffset

                        for i, ii in (
                                ('AttachmentOffset.Rotation.Angle',
                                 f'LVarset.{XObject[1][1]}AttOffAngle'),
                                ('AttachmentOffset.Base.x',
                                 f'LVarset.{XObject[1][1]}AttOffPosX'),
                                ('AttachmentOffset.Base.y',
                                 f'LVarset.{XObject[1][1]}AttOffPosY'),
                                ('AttachmentOffset.Base.z',
                                 f'LVarset.{XObject[1][1]}AttOffPosZ')):
                            ogg.setExpression(i, ii)
                            b = 0

                    elif "Placement" in Property[0]:  # Check if it is an Placement

                        for i, ii in (
                                ('Placement.Rotation.Angle',
                                 f'LVarset.{XObject[1][1]}PlacementAngle'),
                                ('Placement.Base.x',
                                 f'LVarset.{XObject[1][1]}PlacementPosX'),
                                ('Placement.Base.y',
                                 f'LVarset.{XObject[1][1]}PlacementPosY'),
                                ('Placement.Base.z',
                                 f'LVarset.{XObject[1][1]}PlacementPosZ')):
                            ogg.setExpression(i, ii)
                            b = 0  # NOTE: Is this used!!!

                    else:
                        try:  # check if it is a modifiable constraint
                            ogg.getDatum(Property[0])
                            if "Constraint" in Property[0]:
                                # e.g. ‘Constraint6’ try to see if the constraint
                                # does not have a name
                                aa = f"Constraints[{int(Property[0][10:])-1}]"
                                Expression = f'LVarset.{XObject[1][1]}{Property[0]}'

                                ogg.setExpression(aa, Expression)
                                # e.g. <Sketcher::SketchObject>.setExpression(
                                # Constraint[6], ‘LVarset.   Sketch_Constraint6’)
                            else:
                                # if there is not Constraint in the name
                                # then it's a constraint with a name' like
                                # es. 'BoxLenght'
                                aa = f"Constraints[{ogg.getIndexByName(Property[0])}]"
                                Expression = f'LVarset.{XObject[1][1]}{Property[0]}'
                                ogg.setExpression(aa, Expression)
                        except Exception as e:
                            # if it is not a Constraint(Datum) then it is
                            # a Property' type e.g. Value or Occurrence
                            Expression = f'LVarset.{XObject[1][1]}{Property[0]}'
                            ogg.setExpression(Property[0], Expression)
                            # es. <Sketcher::SketchObject>.setExpression(
                            # Largh, 'LVarset.Sketch_Largh')

                    # removes Property from Objects so that it is no longer listed
                    Objects[Objects.index(XObject)].remove(Property)
                else:
                    # otherwise remember not to delete the entire XObject
                    x = 1

            if x == 0:
                # If there are no more Properties, remove XObject from Objects
                Objects.remove(XObject)
            c = 3
        # self.NObject = 0
        d.recompute()
        # self.ListProperties.clear()
        XObject = []
        self.XObjects = []

        self.ListProperties.clear()
        self.ObjComb.clear()
        self.NOgg = -1

# ------------------------------------------------
#                  code execution
# ------------------------------------------------


Window1 = Window1()
screen = Window1.screen().availableGeometry()
x = screen.x() + (screen.width() - Window1.width()) // 3
y = screen.y() + (screen.height() - Window1.height()) // 5
Window1.move(x, y)
Window1.show()
