import numpy as np
import math
import matplotlib.pyplot as plt

class GiftWrap():

    def converter(arr):
        #np array to 2d list for giftwrap
        length = int (np.size(arr)/2)
        new_arr = []
        for i in range(length):
            new_arr.append([arr[i,0],arr[i,1]])
        return new_arr

    def orientation(p1, p2, p3):
        x1, y1, x2, y2, x3, y3 = *p1, *p2, *p3
        d = (y3-y2)*(x2-x1) - (y2-y1)*(x3-x2)
        if d > 0:
            return 1
        elif d < 0:
            return -1
        else:
            return 0  

    def dist(p1, p2):
        x1, y1, x2, y2 = *p1, *p2
        return math.sqrt((y2-y1)**2 + (x2-x1)**2)  

    def gift_wrapping(points):
        points = GiftWrap.converter(points)
        on_hull = min(points)
        hull = []
        while True:
            hull.append(on_hull)
            next_point = points[0]
            for point in points:
                o = GiftWrap.orientation(on_hull, next_point, point)
                if next_point == on_hull or o == 1 or (o == 0 and GiftWrap.dist(on_hull, point) > GiftWrap.dist(on_hull, next_point)):
                    next_point = point
            on_hull = next_point
            if on_hull == hull[0]:
                break
        return hull

def centroid(sheep):

        x = sheep[:,0]
        x_cg = sum(x)/len(x)
        y = sheep[:,1]
        y_cg = sum(y)/len(y)
        return x_cg,y_cg

def interpolate(coord1, coord2, n):

    x1, y1 = coord1
    x2, y2 = coord2
    
    # Calculate the step size for x and y
    dx = (x2 - x1) / (n-1)
    dy = (y2 - y1) / (n-1)
    
    # Generate the list of interpolated points
    interpolated_points = []
    for i in range(n):
        x = x1 + i*dx
        y = y1 + i*dy
        interpolated_points.append([x, y])
        
    return interpolated_points

def interpolate_points(points, num_points):
    interpolated_points = []
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        segment_points = interpolate(p1, p2, num_points)
        interpolated_points.extend(segment_points)
    return interpolated_points

def offset(p,m,y_cg,x_cg,d):
    x0 = p[0]
    y0 = p[1]
    c = y0 - m*x0
    x1_1 = d/np.sqrt(1+m**2) + x0
    x1_2 = -d/np.sqrt(1+m**2) + x0
    y1_1 = m*x1_1 + c
    y1_2 = m*x1_2 + c
    dist21 = (x1_1-x_cg)**2 + (y1_1-y_cg)**2
    dist22 = (x1_2-x_cg)**2 + (y1_2-y_cg)**2
    if dist21>dist22:
        return x1_1,y1_1
    return x1_2,y1_2

def pathfinder(points,d,x_cg,y_cg):
    path = []
    for i in range (len(points)-1):
        m = (points[i+1][1]-points[i][1])/(points[i+1][0]-points[i][0])
        grad = -1/m
        (x1, y1) = offset(points[i],grad,x_cg,y_cg,d)
        (x2, y2) = offset(points[i+1],grad,x_cg,y_cg,d)
        path.append([x1,y1])
        path.append([x2,y2])
    return path

def get_targets(path):
    targets = []
    for i in range(len(path)):
        p1 = path[i]
        p2 = path[(i+1)%len(path)]
        dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        num = int(dist // 20) + 2
        interpolated = interpolate_points([p1,p2],num)
        targets.extend(interpolated)
    return targets

def navigate_loop(points, drone1_pos, drone2_pos):
    """Given a loop defined by a list of points, navigate two drones in the same direction"""
    points_arr = np.array(points)
    drone1_pos_arr = np.array(drone1_pos)
    drone2_pos_arr = np.array(drone2_pos)

    # Find the indices of the current drone positions
    drone1_index = np.argmin(np.sum((points_arr - drone1_pos_arr)**2, axis=1))
    drone2_index = np.argmin(np.sum((points_arr - drone2_pos_arr)**2, axis=1))

    # Determine the indices of the next points for each drone, wrapping around to the beginning of the loop if necessary
    next_index1 = (drone1_index + 2) % len(points)
    next_index2 = (drone2_index + 2) % len(points)

    # Compute the coordinates of the next points
    next_pos1 = tuple(points[next_index1])
    next_pos2 = tuple(points[next_index2])

    # Return the positions of the two drones
    return next_pos1, next_pos2

