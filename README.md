# LVarset
a macro for FreeCAD Varset

The macro I enjoyed writing, does this:
it analyzes all the objects in the FreeCAD drawing and creates a window where one can choose among all the objects of the drawing and select all the Properties one is interested in, and then import them into a varset, that will be created automatically. 
then the macro will populates it with all the selected objects and properties and enters a formulas into the drawing for each properties, binding the object properties to the varset properties.
In this way, changing the value of the varset properties changes the dimensions (or rotation if you selected it) of the object in the drawing.

the object name goes in the varset group name and the properties of the object goes in the list of that group

INSTALLATION:

put the 3 files LVarset_0_1_Beta.py, Lvarset.ui, Lvarset.svg in the macro folder of your Freecad program eg. "C:\Users\�your_Name�\AppData\Roaming\FreeCAD\Macro"

use it with the menu MACRO or:

right click in the toolbar --> customize� --> tab MACROS � Select the LVarset_0_1_Beta.py in the input field Macro: -- write Lvarset in the menu text: field -->  ADD button  --> press the three dot pixmap button -� press the icon folder� button --> plus button --> select the macro folder (eg. "C:\Users\your_Name�\AppData\Roaming\FreeCAD\Macro") --> ok button --> choose the Lvarset icon --> click the tool bars tab --> in the right combobox choose the GLOBAL ambient --> new button --> choose a name tor the new toolbar --> ok button --> now in the left combobox choose the macro ambient --> in the left window choose the Lvarset icon --> click the right arrow --> and finally the close button. The Lvarset icon will appear in the tool bar and you can press it to execute the macro.

