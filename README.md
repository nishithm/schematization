Schematization Plug-in for QGIS
===============================

This is part of GSOC 2014 project for QGIS under Open Source Geospatial Foundation (OSGEO).

For weekly reports and more details check - http://hub.qgis.org/wiki/quantum-gis/nishithm

A detailed report of the project can be seen at - https://dl.dropboxusercontent.com/u/86965637/schematization_gsoc2014.pdf

How to install
---------------
1. Clone the repository or download the zip file from https://github.com/nishithm/schematization/archive/master.zip and extract it.
2. Copy and paste the folder in the '.qgis2/python/plugins/' folder which would be in the home directory of the user (this is same for both Windows as well as any Linux system). Also change the name of the folder to 'schematization'.
3. Now in the QGIS this plugin would show under 'Manage and Install Plugins' and would just needed to be activated there. (As this is an experimental plugin, please make sure that you have the 'Show also experimental plugins' box checked under the 'Settings').
4. Make sure that the **Activate** option for 'Schematization Algorithms' is checked under *Processing > Options > Providers*.


How to use
-----------
The plugin would show in the processing toolbox with the name 'Schematization Algorithms' and there will be two algorithm groups under it.

1. One would be 'Algorithms for simplifying layer' under which the 'Topology Preserving Simplifier' algorithm is there. This algorithm takes as input a line vector layer and has a parameter 'Threshold' which the user can give as input (default is set to 2000) and returns a simplified form of the input while preserving the topology. The degree of simplification that will take place will depend on the value if the 'Threshold'.
2. The other group 'Algorithms for applying constraints' will have 'Applying Angle Constraints'. This algorithm applies the angle/direction constraint on the simplified layer (obtained from 'Topology Preserving Simplifier' algorithm). The constraint is applied in a manner such that the final output has lines oriented in either horizontal, vertical or diagonal direction. This satisfies one of the conditions for schematization and makes the map easier to read and understand.
3. The algorithm can be run again on the resultant dataset. It gives better results in some cases.

The ideal way would be to run the 'Topology Preserving Simplifier' first with an applicable value of threshold and then run the 'Applying Angle Constraints'.
