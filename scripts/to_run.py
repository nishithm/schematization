from math import pi, atan2, cos, sin, atan

# To get Features

def get_feature(iface):
    
    layer = iface.activeLayer()
    iter = layer.getFeatures()
    
    # length of lines
    lines = []
    
    # Geometry of lines
    att_line = []
    
    # Intersecting lines' id
    mat_id = []
    
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
        
    xx = att_line[x]
    
    for i in range(0,len(lines)):
        if (att_line[i] != xx):
            if ( att_line[i][0] == xx[0] ):
                mat_id.append(i)
                
            if (att_line[i][1] == xx[0]):
                mat_id.append(i)

    ans = [layer, att_line, lines, x]                
    return ans

# --------------------------------------------------
# Functions  for roatation

# Find Intersecting lines
def find_intersect(att_line, ref_line, fid):
    intersect = [ [], [], [], [] ]
    
    for i in range(0,len(att_line)):
        if (i!=fid) and (i not in MA):
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

def pre_rot(att_line, intersect, ref_line, lines_len):
    att_line = rotate_l(att_line, intersect[0], ref_line, lines_len, 1,0)
    att_line = rotate_l(att_line, intersect[1], ref_line, lines_len, 0,0)
    att_line = rotate_l(att_line, intersect[2], ref_line, lines_len, 1,1)
    att_line = rotate_l(att_line, intersect[3], ref_line, lines_len, 0,1)
    return att_line
    
                
def rotate_l(att_line, intersect, ref_line, lines_len, fl2, fl):
    
    ang1 = atan2( (ref_line[0][1] - ref_line[1][1]) , (ref_line[0][0] - ref_line[1][0]) )
     
    for i in intersect:
        p = att_line[i][fl2]
        ang2 = atan2( ref_line[fl][1] - p[1], ref_line[fl][0] - p[0]) 
    
        ang3 = ang1-ang2
    
        if (ang3 > pi):
            ang3 = ang3 - (2*pi)
        elif (ang3 < (-1)*pi):
            ang3 = (2*pi) + ang3
        
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
            
    
        finang = pi + ang1 - newang
    
        MA.append(i)
    
        newp = QgsPoint( ref_line[fl][0] + ( lines_len[i] * cos(finang)) , ref_line[fl][1] + ( lines_len[i] * sin(finang)) )
        att_line[i][fl2] = newp
    
        for j in range(0,len(att_line)):
            if att_line[j][0] == p :
                att_line[j][0] = newp
            elif att_line[j][1] == p :
                att_line[j][1] = newp
            
    return att_line
              
              

#____________________________________

ans = get_feature(iface)

layer = ans[0]
att_line = ans[1]
lines = ans[2] 
ffid = ans[3]

MA = []
MA.append(ffid)

for m in MA :
    iint = find_intersect(att_line, att_line[m], m)
    A = pre_rot(att_line, iint, att_line[m], lines) 
    
    for i in range(0,len(att_line)) :
        g = QgsGeometry.fromPolyline(A[i])
        layer.dataProvider().changeGeometryValues({ i : g })
    
