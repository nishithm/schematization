Schematization Plug-in for QGIS
===============================

This is part of GSOC 2014 project for QGIS under Open Source Geospatial Foundation (OSGEO).

more details at - http://hub.qgis.org/wiki/quantum-gis/nishithm


How to install
---------------
1. Clone the repository or download the zip file from https://github.com/nishithm/schematization/archive/master.zip and extract it.
2. Copy and paste the folder in the '.qgis2/python/plugins/' folder which would be in the home directory of the user (this is same for both Windows as well as any Linux system). Also change the name of the folder to 'schematization'.
3. Now in the QGIS this plugin would show under 'Manage and Install Plugins' and would just needed to be activated there. (As this is an experimental plugin, please make sure that you have the 'Show also experimental plugins' box checked under the 'Settings').


How to use
-----------
The plugin would show in the processing toolbox with the name 'Schematization Algorithms' and there will be two algorithm groups under it.

1. One would be 'Algorithms for simplifying layer' under which the 'Topology Preserving Simplifier' algorithm is there. This algorithm takes as input a line vector layer and returns a simplified form of the input while preserving the topology.
2. The other group 'Algorithms for applying constraints' will have 'Applying Angle Constraints'. This algorithm applies the angle/direction constraint on the simplified layer (obtained from 'Topology Preserving Simplifier' algorithm). The constraint is applied in a manner such that the final output has lines oriented in either horizontal, vertical or diagonal direction. This satisfies one of the conditions for schematization and makes the map easier to read and understand.
