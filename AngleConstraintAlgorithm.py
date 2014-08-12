# -*- coding: utf-8 -*-

"""
***************************************************************************
    AngleConstraintAlgorithm.py
    ---------------------
    Date                 : August 2014
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
__date__ = 'August 2014'
__copyright__ = '(C) 2014, Nishith Maheshwari'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from math import pi, atan2, cos, sin, atan


from processing.core.Processing import Processing
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.parameters.ParameterVector import ParameterVector
from processing.outputs.OutputVector import OutputVector
from processing.tools import dataobjects, vector
from processing.parameters.ParameterString import ParameterString
import processing


class AngleConstraintAlgorithm(GeoAlgorithm):
    
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    
    D1 = {}
    D2 = {}
    MA = []
    MB = {}
    B = []

    # Copy Layer
    def cpy_layer_feat( self , L , s):
    #  This is a function to return a copy of the input layer 'L'
    #  Parameters : Input Layer = L , Name of the layer = s, Output Layer (copy) = ans
    
        ans = QgsVectorLayer("LineString?crs=epsg:%d" % L.crs().postgisSrid(),s,"memory")
        ans.startEditing()
        W = ans.dataProvider()
        W.addAttributes( [ QgsField("cat",QVariant.Int) ] )
        
        I = L.getFeatures()
        
        for i in I:
            W.addFeatures([i])
            
        ans.commitChanges()
        ans.updateExtents()
        
        return ans


    # Create spatial index
    def spat_ind(self, layer):
    #  This function returns the spatial index of the layer 'layer'
    
        ind = QgsSpatialIndex()
        iter = layer.getFeatures()
        for i in iter:
            ind.insertFeature(i)
    
        return ind
    
    
    def touches_cond(self, lay, D, ind):
    # This function populates the dictionary 'D' with the intersection data of layer 'lay' using the spatial index 'ind'
    #  The data is stored in the dictionary in the form " D[4] will contain a list of the ids of the features which intersect the feature with id=4 " 
    
        iterr = lay.getFeatures()
        allfeatures = {}
        
        for feaa in iterr:
            allfeatures[feaa.id()] = feaa
        
        
        for f in allfeatures.values():
            D[f.id()] = []
            iids = ind.intersects(f.geometry().boundingBox())
            
            for iid in iids:
                ff = allfeatures[iid]
                if ff == f: continue
                touches = ff.geometry().intersects(f.geometry())
                if touches:
                    D[f.id()].append(iid)
            
            D[f.id()].sort()
    
    
    
    #Get Feature list for iterations etc
    def get_feature(self, layer):
        
        iter = layer.getFeatures()
          
        # length of lines
        lines = []
        
        # Geometry of lines
        att_line = []
         
            
        for feature in iter:
            # fetch geometry        
            geom = feature.geometry()
        
            if geom.type() == QGis.Line:
              x = geom.asPolyline()
              att_line.append(x)
              line_len = geom.length()
              lines.append(line_len)
                
        for i in range (0,len(lines)):
            if(lines[i] == max(lines)):
                x = i
                # x = id of Longest line 
            
        xx = att_line[x]
    
        ans = [layer, att_line, lines, x]                
        return ans
    
    
    # Find intersections
    def find_intersect(self, att_line, ref_line, fid):
    # This function returns a list of lists of ids of features intersecting ref_line
        intersect = [ [], [], [], [] ]
        
        for i in range(0,len(att_line)):
            if (i!=fid) and (self.MB[i]==0):
                if (att_line[i][0] == ref_line[0]):
                    intersect[0].append(i)
                elif (att_line[i][1] == ref_line[0]):                   
                    intersect[1].append(i)
                elif (att_line[i][0] == ref_line[1]):
                    intersect[2].append(i)
                elif (att_line[i][1] == ref_line[1]):
                    intersect[3].append(i)
            
        return intersect
    
    # Rotate line                
    def rotate_l(self, att_line, intersect, ref_line, lines_len, fl2, fl):
    # This function takes in input : att_line = list of geometries of lines, intersect = a list of ids which intersect ref_line,
    #                                ref_line = reference/base line, lines_len = list of length of lines,
    #                                fl and fl2 = flags which determines at which point the intersection is taking place
    
        p = att_line[intersect][fl2]
        
        # ang = angle of the line to be oriented (slope)
        ang = atan2( ref_line[fl][1] - p[1], ref_line[fl][0] - p[0]) 
    
        if (ang > pi):
            ang = ang - (2*pi)
        elif (ang < (-1)*pi):
            ang = (2*pi) + ang
        
        
        # This if-else part computes 'newang' which is the desired angle between 
        # the two lines which is closest to the current angle between them.
        if ( ( ang >= (-1)*pi ) and ( ang <= (-7)*pi/8.00) ):
            newang = (-1)*pi
        elif ( ( ang > (-7)*pi/8.00 ) and ( ang <= (-5)*pi/8.00) ):
            newang = (-3)*pi/4.00
        elif ( ( ang > (-5)*pi/8.00 ) and ( ang <= (-3)*pi/8.00) ):
            newang = (-1)*pi/2.00
        elif ( ( ang > (-3)*pi/8.00 ) and ( ang <= (-1)*pi/8.00) ):
            newang = (-1)*pi/4.00
        elif ( ( ang > (-1)*pi/8.00 ) and ( ang <= pi/8.00)):
            newang = 0
        elif ( ( ang > pi/8.00 ) and ( ang <= 3*pi/8.00)):
            newang = pi/4.00
        elif ( ( ang > 3*pi/8.00 ) and ( ang <= 5*pi/8.00)):
            newang = pi/2.00
        elif ( ( ang > 5*pi/8.00 ) and ( ang <= 7*pi/8.00)):
            newang = 3*pi/4.00
        elif ( ( ang > 7*pi/8.00 ) and ( ang <= pi)):
            newang = pi
            
    
        # finang = angle of the oriented line (slope) 
        finang = pi + newang
    
        self.MA.append(intersect)
        self.MB[intersect] = 1
        
        # newp = the new point of the end which is rotated 
        newp = QgsPoint( ref_line[fl][0] + ( lines_len[intersect] * cos(finang)) , ref_line[fl][1] + ( lines_len[intersect] * sin(finang)) )
        att_line[intersect][fl2] = newp
    
        # changing to the 'newp' in all the lines having the point which is to be rotated
        for j in range(0,len(att_line)):
            if att_line[j][0] == p :
                att_line[j][0] = newp
                if self.MB[j] == 2:
                    self.MB[j] = 0
                
                
            elif att_line[j][1] == p :
                att_line[j][1] = newp
                if self.MB[j] == 2:
                    self.MB[j] = 0
                
        return att_line
    


    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Applying Angle constraint'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Algorithms for applying constraints'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
                       'Layer with Angle constraints'))

    def processAlgorithm(self, progress):

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        layer = dataobjects.getObjectFromUri(inputFilename)
        
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        provider = layer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding,
                                     provider.fields(),
                                     provider.geometryType(), provider.crs())              
        
       
                        
        # Copying the input layer to temp1 and temp2
        temp1 = self.cpy_layer_feat(layer,"temp1")
        temp2 = self.cpy_layer_feat(layer,"temp2")
        
        t1 = self.get_feature(temp1)
        t2 = self.get_feature(temp2)
        
        a1 = t1[1]
        lines1 = t1[2] 
        ffid1 = t1[3]
        
        
        for i in range(0, len(a1)):
            b = QgsGeometry.fromPolyline(a1[i])
            self.B.append(b.asPolyline())


        for i in range(0,len(a1)):
            self.MB[i] = 0
        
        self.MA.append(ffid1)
        fff = 1
        for m in self.MA :
            self.MB[m] = 2
            if fff :
                iint = [ [] , [] , [] , [m] ]
                fff=0
            else :
                iint = self.find_intersect(a1, a1[m], m)
                
            
            ff1 = 1
            ff2 = 0
            for j in range(0,4):
                if j>1:
                    ff2 = 1
                
                for inter_sect in iint[j]:
                    
                    A = self.rotate_l(a1, inter_sect, a1[m], lines1, ff1 ,ff2)                    
                
                    for i in range(0,len(a1)) :
                        g = QgsGeometry.fromPolyline(A[i])
                        temp2.dataProvider().changeGeometryValues({ i+1 : g })
                    
                
                    s2 = self.spat_ind(temp2)
                    self.touches_cond( temp2, self.D2, s2)
                    
                    s1 = self.spat_ind(temp1)
                    self.touches_cond( temp1 , self.D1, s1)
                    
                
                    if self.D1==self.D2:
                        iter_temp = temp2.getFeatures()
                        temp1.startEditing()        
                        for i in range(0,len(a1)) :
                            gg = QgsGeometry.fromPolyline(A[i])
                            temp1.dataProvider().changeGeometryValues({ i+1 : gg })
                        
                            b = QgsGeometry.fromPolyline(a1[i])
                            self.B[i] = b.asPolyline()
                        
                    
                        temp1.commitChanges()
                    
                    else:
                        for i in range(0,len(a1)):
                            b = QgsGeometry.fromPolyline(self.B[i])
                            a1[i] = b.asPolyline()
                
                ff1 = 1 - ff1
    
        FF = temp1.getFeatures()
        for f in FF :
            writer.addFeature(f)
    
