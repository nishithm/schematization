# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014 by Nishith Maheshwari
    Email                : nshthm at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Nishith Maheshwari'
__date__ = 'May 2014'
__copyright__ = '(C) 2014, Nishith Maheshwari'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from processing.core.Processing import Processing
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.parameters.ParameterVector import ParameterVector
from processing.outputs.OutputVector import OutputVector
from processing.tools import dataobjects, vector
from processing.parameters.ParameterString import ParameterString
import processing


class SimplificationAlgorithm(GeoAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    THRES = 'THRES'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Topology Preserving Simplifier'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Algorithms for simplifying layers'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))
        
        self.addParameter(ParameterString(self.THRES, 'Threshold', default=2000))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
                       'Simplified output layer'))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)
        thres = self.getParameterValue(self.THRES)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        
        inputLayer = dataobjects.getObjectFromUri(inputFilename)
        
        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        provider = inputLayer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding,
                                     provider.fields(),
                                     provider.geometryType(), provider.crs())              
        
        progress.setText('Dissolving Layer')
        # Calling the Dissolve algorithm of processing
        dissolved =  processing.runalg("qgis:dissolve", inputLayer, True, '', None)['OUTPUT']
        dissolvedLayer = processing.getObject(dissolved)

        progress.setPercentage(25)
        
        progress.setText('Converting from Multipart to Single parts')
        # Calling the MultipartToSinglepart algorithm of processing
        multi = processing.runalg("qgis:multiparttosingleparts", dissolvedLayer, None)['OUTPUT']
        vectorLayer = processing.getObject(multi)
        
        progress.setPercentage(50)

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        features = vectorLayer.getFeatures()
                
        #From here the code of script starts
        
        f = QgsFeature()
 
        # Now we take the first feature from layer and create a new geometry copied from geometry of that feature
        features.nextFeature(f)
        geom = QgsGeometry(f.geometry())
        
        # Geometry must be multipart
        geom.convertToMultiType()
 
        progress.setText('Adding geometries...')
        i = 0
        count = 25./vectorLayer.featureCount()
        # Now we iterate over other features and add their geometries as parts of our multipart geometry
        for f in features:
            geom.addPartGeometry(f.geometry())
            progress.setPercentage(50+(i*count))
            i += 1
        
        # To Simplify geometry
        s = QgsTopologyPreservingSimplifier(float(thres))
        s_geom = s.simplify(geom)   
        
        # Now we save simplified parts as separate features
        progress.setText('Simplifying parts...')
        s_geom_list = s_geom.asMultiPolyline()
        count = 25./len(s_geom_list)
        i = 0
        for part in s_geom_list:
            f = QgsFeature()
            f.setGeometry( QgsGeometry.fromPolyline(part) )
            writer.addFeature(f)
            progress.setPercentage(75+(i*count))
            i += 1
            
        progress.setText('Simplification done !!')
                       
        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model
