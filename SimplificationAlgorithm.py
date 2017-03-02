# -*- coding: utf-8 -*-

"""
***************************************************************************
    SimplificationAlgorithm.py
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
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from processing.core.parameters import ParameterString
import processing


class SimplificationAlgorithm(GeoAlgorithm):
    """This is an algorithm that takes a vector layer and creates
    a new layer which is a simplified version of the input.
    """

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    THRES = 'THRES'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
       
        # The name that the user will see in the toolbox
        self.name = 'Topology Preserving Simplifier'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Algorithms for simplifying layers'

        # We add the input vector layer.
        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))
        
        self.addParameter(ParameterString(self.THRES, 'Threshold', default=2000))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
                       'Simplified output layer'))

    def processAlgorithm(self, progress):

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
        
        # And now we can start the processing part

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        provider = inputLayer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding,
                                     provider.fields(),
                                     provider.geometryType(), inputLayer.crs())              
        
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

        features = vectorLayer.getFeatures()
                      
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
