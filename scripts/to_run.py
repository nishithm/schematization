from math import pi, atan2, cos, sin, atan
from PyQt4.QtCore import *

# To run the algorithm first run the script in the Qgis python console and then in the console run the function 'nash' 


# Copy Layer
def cpy_layer_feat( L , s):
    
#  This is a function to return a copy of the input layer 'L'
#  Parameters : Input Layer = L , Name of the layer = s, Output Layer (copy) = ans

    ans = QgsVectorLayer("LineString",s,"memory")
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
def spat_ind(layer):
    
#  This function returns the spatial index of the layer 'layer'

    ind = QgsSpatialIndex()
    iter = layer.getFeatures()
    for i in iter:
        ind.insertFeature(i)

    return ind


def touches_cond( lay, D, ind):

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
def get_feature(layer):
    
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
            print i , max(lines)
            x = i
            # x = id of Longest line 
        
    xx = att_line[x]

    ans = [layer, att_line, lines, x]                
    return ans


# Find intersections
def find_intersect(att_line, ref_line, fid):

# This function returns a list of lists of ids of features intersecting ref_line
    intersect = [ [], [], [], [] ]
    
    for i in range(0,len(att_line)):
        if (i!=fid) and (MB[i]==0):
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
def rotate_l(att_line, intersect, ref_line, lines_len, fl2, fl):
    
# This function takes in input : att_line = list of geometries of lines, intersect = a list of ids which intersect ref_line,
#                                ref_line = reference/base line, lines_len = list of length of lines,
#                                fl and fl2 = flags which determines at which point the intersection is taking place

    # ang1 = angle of reference line (slope)
    ang1 = atan2( (ref_line[0][1] - ref_line[1][1]) , (ref_line[0][0] - ref_line[1][0]) )
     
    for i in intersect:
        p = att_line[i][fl2]
        
        # ang2 = angle of the line to be oriented (slope)
        ang2 = atan2( ref_line[fl][1] - p[1], ref_line[fl][0] - p[0]) 
    
        # ang3 = angle between the reference line and the intersecting line
        ang3 = ang1-ang2
    
        if (ang3 > pi):
            ang3 = ang3 - (2*pi)
        elif (ang3 < (-1)*pi):
            ang3 = (2*pi) + ang3
        
        
        # This if-else part computes 'newang' which is the desired angle between the two lines which is closest to the current angle between them.
        if ( ( ang3 >= (-1)*pi ) and ( ang3 <= (-7)*pi/8.00) ):
            newang = (-1)*pi
        elif ( ( ang3 > (-7)*pi/8.00 ) and ( ang3 <= (-5)*pi/8.00) ):
            newang = (-3)*pi/4.00
        elif ( ( ang3 > (-5)*pi/8.00 ) and ( ang3 <= (-3)*pi/8.00) ):
            newang = (-1)*pi/2.00
        elif ( ( ang3 > (-3)*pi/8.00 ) and ( ang3 <= (-1)*pi/8.00) ):
            newang = (-1)*pi/4.00
        elif ( ( ang3 > (-1)*pi/8.00 ) and ( ang3 <= pi/8.00)):
            newang = 0
        elif ( ( ang3 > pi/8.00 ) and ( ang3 <= 3*pi/8.00)):
            newang = pi/4.00
        elif ( ( ang3 > 3*pi/8.00 ) and ( ang3 <= 5*pi/8.00)):
            newang = pi/2.00
        elif ( ( ang3 > 5*pi/8.00 ) and ( ang3 <= 7*pi/8.00)):
            newang = 3*pi/4.00
        elif ( ( ang3 > 7*pi/8.00 ) and ( ang3 <= pi)):
            newang = pi
            
    
        # finang = angle of the oriented line (slope) 
        finang = pi + ang1 - newang
    
        MA.append(i)
        MB[i] = 1
        
        # newp = the new point of the end which is rotated 
        newp = QgsPoint( ref_line[fl][0] + ( lines_len[i] * cos(finang)) , ref_line[fl][1] + ( lines_len[i] * sin(finang)) )
        att_line[i][fl2] = newp
    
        # changing to the 'newp' in all the lines having the point which is to be rotated
        for j in range(0,len(att_line)):
            if att_line[j][0] == p :
                att_line[j][0] = newp
                if MB[j] == 2:
                    MB[j] = 0
                
                
            elif att_line[j][1] == p :
                att_line[j][1] = newp
                if MB[j] == 2:
                    MB[j] = 0
            
    return att_line






#Global Variables

# Dictionary D1 and D2 store the intersection details of 'temp1' and 'temp2' respectively. 
# They will be used to determine whether the number of intersections changed after the orientation of a feature
D1 = {}
D2 = {}
    
# MA = List of ids of the features which will be considered as base and the lines around it will be oriented. 
#    It starts with only the longest feature's id in it and is continuously getting appended in function 'rotate_l'
# MB = A dictionary which keeps the record that whether the line has been considered as base (value=2), has been oriented (value=1) or not (value=0)
MA = []
MB = {}
    
# B = Stores the polyline data of the output layer
B = []


 

def nash():
    c=0
    c1=0
    layer = iface.activeLayer()
    
    # Copying the input layer to temp1 and temp2
    temp1 = cpy_layer_feat(layer,"temp1")
    temp2 = cpy_layer_feat(layer,"temp2")
    
    t1 = get_feature(temp1)
    t2 = get_feature(temp2)
    
    a1 = t1[1]
    lines1 = t1[2] 
    ffid1 = t1[3]
    
    
    for i in range(0, len(a1)):
        b = QgsGeometry.fromPolyline(a1[i])
        B.append(b.asPolyline())
    
    
    
    
    for i in range(0,len(a1)):
        MB[i] = 0
    
    MA.append(ffid1)
    
    for m in MA :
        MB[m] = 2
        iint = find_intersect(a1, a1[m], m)
        
        ff1 = 1
        ff2 = 0
        for j in range(0,4):
            if j>1:
                ff2 = 1
            A = rotate_l(a1, iint[j], a1[m], lines1, ff1 ,ff2)
            ff1 = 1 - ff1
            
        
            for i in range(0,len(a1)) :
                g = QgsGeometry.fromPolyline(A[i])
                temp2.dataProvider().changeGeometryValues({ i+1 : g })
            
        
            s2 = spat_ind(temp2)
            touches_cond( temp2, D2, s2)
            
            s1 = spat_ind(temp1)
            touches_cond( temp1 , D1, s1)
            
        
            if D1==D2:
                c+=1
                iter_temp = temp2.getFeatures()
                temp1.startEditing()        
                for i in range(0,len(a1)) :
                    gg = QgsGeometry.fromPolyline(A[i])
                    temp1.dataProvider().changeGeometryValues({ i+1 : gg })
                
                    b = QgsGeometry.fromPolyline(a1[i])
                    B[i] = b.asPolyline()
                
            
                temp1.commitChanges()
            
            else:
                c1+=1
                print j, m
                for i in range(0,len(a1)):
                    b = QgsGeometry.fromPolyline(B[i])
                    a1[i] = b.asPolyline()
            
    print c
    print c1
    QgsMapLayerRegistry.instance().addMapLayer(temp1)

                
