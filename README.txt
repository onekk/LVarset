# LVarset
a macro for FreeCAD Varset

The macro I enjoyed writing, does this:
it analyzes all the objects in the FreeCAD drawing and creates a window where one can choose among all the objects of the drawing and select all the Properties one is interested in, and then import them into a varset, that will be created automatically. 
then the macro will populates it with all the selected objects and properties and enters a formulas into the drawing for each properties, binding the object properties to the varset properties.
In this way, changing the value of the varset properties changes the dimensions (or rotation if you wish) of the object in the drawing.

the object name goes in the varset group name and the properties of the object goes in the list of that group
