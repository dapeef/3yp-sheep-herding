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

class Bucket():

    def centroid(sheep):
        x = sheep[:,0]
        x_cg = sum(x)/len(x)
        y = sheep[:,1]
        y_cg = sum(y)/len(y)
        return x_cg,y_cg

    def dist(arr,gate_pos):
        distances = []
        for i in range(0,len(arr)):
            distances.append(np.sqrt((arr[i][0]-gate_pos[0])**2+(arr[i][1]-gate_pos[1])**2))
        return distances

    def get_nodes(x_cg,y_cg,gate_pos,hull,angle):
        m1 = (y_cg - gate_pos[1])/(x_cg - gate_pos[0])
        c = y_cg - m1*x_cg
        centroid_dist = np.sqrt((x_cg - gate_pos[0])**2 + (y_cg - gate_pos[1])**2)
        dists = Bucket.dist(hull,gate_pos)
        # new_hull = [i for i in hull if i in dists >= centroid_dist]
        new_hull = []
        for i in range(len(hull)):
            if dists[i] >= centroid_dist:
                new_hull.append(hull[i])
        hull1,hull2 = [],[]
        for n in new_hull:
            if n[1] >= m1*n[0] + c:
                hull1.append(n)
            else:
                hull2.append(n)
        grads1,grads2,angles1,angles2 = [],[],[],[]
        for i in range(len(hull1)):
            grads1.append((hull1[i][1]-y_cg)/(hull1[i][0]-x_cg))
            angles1.append(abs(math.atan((grads1[i]-m1)/(1+m1*grads1[i]))))
        for i in range(len(hull2)):
            grads2.append((hull2[i][1]-y_cg)/(hull2[i][0]-x_cg))
            angles2.append(abs(math.atan((grads2[i]-m1)/(1+m1*grads2[i]))))
        error1 = [n - angle for n in angles1]
        abs_err1 = [abs(ele) for ele in error1]
        error2 = [n - angle for n in angles2]
        abs_err2 = [abs(ele) for ele in error2]
        if hull1 == []:
            node1 = [0,0]
        else:
            node1 = hull1[np.argmin(abs_err1)]
        if hull2 == []:
            node2 = [0,0]
        else:
            node2 = hull2[np.argmin(abs_err2)]
        return node1,node2

    def drone_coords(nodes,x_cg,y_cg,r):
        coords = []
        for i in range(len(nodes)):
            x = nodes[i][0]
            y = nodes[i][1]
            m = (y-y_cg)/(x-x_cg)
            c = y_cg - m*x_cg
            s = np.sqrt((x - x_cg)**2 + (y - y_cg)**2)
            x_new = x_cg +(x-x_cg)*(s+r)/s
            y_new = m*x_new + c
            coords.append([x_new,y_new])
        return coords

    def line(x_cg,y_cg,gate_pos,drone_pos):
        m = (y_cg - gate_pos[1])/(x_cg - gate_pos[0])
        c = drone_pos[1] - m*drone_pos[0]
        return [m,c]

    def converter (arr):
        new_arr = []
        for i in range(len(arr)):
            coords = arr[i][0]
            x = coords.x
            y = coords.y
            new_arr.append([x,y])

    def get_targets(sheep,R_fear,gate_pos,angle):
        # sheep = Bucket.converter(arr)
        # new bit: if sheep is already through gate, ignore
        # subject to change this if random gate position rather than existing setup
        new_sheep = []
        for i in range(len(sheep)):
            # if i >= len(sheep):
            #     break
            # if sheep[i,0] > gate_pos[0]:
            #     # index = [i,:]
            #     sheep = np.delete(sheep,i,axis=0)
            if sheep[i,0] <= gate_pos[0]:
                new_sheep.append(sheep[i,:])
        sheep = np.asarray(new_sheep)                

        hull = GiftWrap.gift_wrapping(sheep)
        x_cg,y_cg = Bucket.centroid(sheep)
        node1,node2 = Bucket.get_nodes(x_cg,y_cg,gate_pos,hull,angle)
        drone_pos = Bucket.drone_coords(nodes=[node1,node2],x_cg=x_cg,y_cg=y_cg,r=R_fear)
        return drone_pos

# R_fear = 0.2
# # remember to put half this distance away from sheep
# velocity = 1
# refresh_rate = 1
# angle = math.pi/6
# # angle = 0

# sheep = np.random.rand(50,2)
# gate_pos = np.array([1.5,-1.5])
# drones = Bucket.get_targets(sheep,R_fear,gate_pos,angle)


# hull = GiftWrap.gift_wrapping(sheep)
# hull = np.asarray(hull)

# drones = np.asarray(drones)
# plt.plot(sheep[:,0],sheep[:,1],'co')
# plt.plot(gate_pos[0],gate_pos[1],c='r',marker='o')
# plt.plot(drones[:,0],drones[:,1],'bo')
# # plt.plot(node1[0],node1[1],'go')
# # plt.plot(node2[0],node2[1],'go')
# # plt.plot(hull[:,0],hull[:,1],'r-')
# # plt.plot(hull1[:,0],hull1[:,1],'mo')
# # plt.plot(hull2[:,0],hull2[:,1],'yo')
# plt.show()