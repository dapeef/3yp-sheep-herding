import numpy as np
import math

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

def get_points(sheep,r):

    hull = GiftWrap.gift_wrapping(sheep)
    x_cg,y_cg = centroid(sheep)
    points = []
    for i in range(len(hull)):
        x = hull[i][0]
        y = hull[i][1]
        m = (y-y_cg)/(x-x_cg)
        c = y_cg - m*x_cg
        s = np.sqrt((x - x_cg)**2 + (y - y_cg)**2)
        x_new = x_cg +(x-x_cg)*(s+r)/s
        y_new = m*x_new + c
        points.append([x_new,y_new])
    return points

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

# def scale_param(current_pos, given_pos, fixed_param):
#     # Calculate the distance between the two positions
#     distance = math.sqrt((current_pos[0] - given_pos[0])**2 + (current_pos[1] - given_pos[1])**2)
    
#     # Scale the parameter based on the distance
#     if distance < 100:
#         scaled_param = fixed_param / 1.05
#     else:
#         scaled_param = fixed_param / (1.05 + 0.85 * (distance - 100) / 900)
    
#     return scaled_param

# def scale_param(current_pos, given_pos, fixed_param, decay_rate=0.1, min_scale=0.5):
#     distance = np.linalg.norm(np.array(current_pos) - np.array(given_pos))
#     if distance < 300:
#         scale_factor = 1/1.05
#     else:
#         scale_factor = 1 / 1.05 * np.exp(-decay_rate * (distance - 300))
#     scale_factor = max(scale_factor, min_scale)
#     scaled_param = fixed_param * scale_factor
#     return scaled_param

def scale_parameter(current_pos, given_pos, fixed_param, dist1, dist2):
    distance = ((current_pos[0] - given_pos[0])**2 + (current_pos[1] - given_pos[1])**2)**0.5
    
    if distance < dist1:
        scale_factor = 1/1.1
    elif distance < dist2:
        scale_factor = (1/1.1) - ((distance - dist1) / (dist2 - dist1)) * ((1/1.1) - (1/1.3))
    else:
        scale_factor = 1/1.3
    
    scaled_param = fixed_param * scale_factor
    return scaled_param


# def roundup(sheep,r,error):
#     index = 0
#     while run= = True:
#         points = get_points(sheep,r)
#         # get drone coords?
#         x = # get fear locations
#         y = # as above
#         s = math.sqrt((x-points[index][0])**2 + (y-points[index][1])**2)
#         if s<=error:
#             index += 1

# testing plots:

# sheep = np.random.rand(50,2)
# plt.plot(sheep[:,0],sheep[:,1],'co')
# points = get_points(sheep,0.2)
# points.append(points[0])
# points = np.asarray(points)
# plt.plot(points[:,0],points[:,1])
# plt.show()