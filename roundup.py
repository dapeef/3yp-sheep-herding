import numpy as np
import matplotlib.pyplot as plt
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