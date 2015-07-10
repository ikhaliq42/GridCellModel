
from image import Position2D
from math import sqrt
#import pdb

def bounding_box(shape):
    ''' 
    Calculates the bounding box that encloses a 2D shape defined 
    by a set of lines.
    Returns the upper left corner and the lower right corner
    Shape is a list of Position2D tuples
    '''
    import pdb; pdb.set_trace()
    min_x = shape[0][0].x
    max_x = shape[0][0].x
    min_y = shape[0][0].y
    max_y = shape[0][0].y
    for line in shape:
        for point in line:
            min_x = min(min_x, point.x)
            max_x = max(max_x, point.x)
            min_y = min(min_y, point.y)
            max_y = max(max_y, point.y)

    #pdb.set_trace()

    return Position2D(min_x, max_y), Position2D(max_x, min_y)
    
def bounding_box_dimensions(shape):
    '''
    Returns the length and height of a  bounding box enclosing a 2D shape
    defined by a set of points.
    Shape is a list of Position2D objects
    '''
    box = bounding_box(shape)
    length = abs(box[1].x - box[0].x)
    height = abs(box[0].y - box[1].y)
    return length, height

def min_dist_to_line(pnt, l):
    return distance(pnt, closest_point_to_line(pnt, l))

def closest_point_to_line(pnt, l):
    '''
    Calculate the minimum distance from point p to line l
    p is a Position2D object.
    l is a tuple of Position2D objects.
    Code adapted from:
    http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    '''

    start = l[0]
    end = l[1]

    d2 = squared_distance(start, end);  # i.e. |start-end|^2 -  avoid a sqrt
    if d2 == 0.0: 
        return pnt   # start == end case    
    else:
        # Consider the line extending the segment, parameterized as start + t (end - start).
        # We find projection of point pnt onto the line. 
        # It falls where t = [(pnt-start) . (end-start)] / |end-start|^2
        t = dotProduct2D(substract2D(pnt, start), substract2D(end, start)) / d2
        if (t < 0.0): 
            return start       # Beyond the 'v' end of the segment
        elif (t > 1.0): 
            return end  # Beyond the 'w' end of the segment
        else:
            j = substract2D(end, start)
            k = Position2D(t * j.x, t * j.y)
            projection = add2D(start, k)  # Projection falls on the segment
            return projection

def scaleLine(originalLine, originalDim, newDim):
    '''
    Scales down a line based on the ratio of two boxes, defined by the
    x and y dimensions of originalDim and newDim
    Points are assumed to be Position2D objects
    '''
    x_ratio = newDim[0] / originalDim[0]
    y_ratio = newDim[1] / originalDim[1]
    start = Position2D(x_ratio * originalLine[0].x, y_ratio * originalLine[0].y)
    end = Position2D(x_ratio * originalLine[1].x, y_ratio * originalLine[1].y)
    return start, end
    

def distance(start, end):
    '''
    Calculate the distance between two points, start and end
    Start and end are Position2D objects
    '''
    return sqrt(squared_distance(start, end))

def squared_distance(start, end):
    '''
    Calculate the squared distance between two points, start and end
    Start and end are Position2D objects
    '''
    z = substract2D(start, end)
    return dotProduct2D(z, z)

def substract2D(p1, p2):
    '''
    Vector subtraction of two Position2D objects
    i.e. subtract p2 from p1
    '''
    return Position2D(p1.x - p2.x, p1.y - p2.y) 

def add2D(p1, p2):
    '''
    Vector addition of two Position2D objects
    i.e. add p2 to p1
    '''
    return Position2D(p1.x + p2.x, p1.y + p2.y)

def dotProduct2D(p1, p2):
    '''
    dot product of 2D vectors given as Position2D objects
    '''
    return p1.x * p2.x + p1.y * p2.y 

