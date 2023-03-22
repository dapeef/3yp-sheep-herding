import numpy as np
import legacy.roundup2 as roundup

def is_point_inside_polygon(point, polygon):
    """
    Determines if a point is inside a polygon using the ray casting algorithm.

    Args:
        point (tuple): A tuple containing the (x, y) coordinates of the point.
        polygon (list): A list of tuples, each containing the (x, y) coordinates of a vertex of the polygon.

    Returns:
        bool: True if the point is inside the polygon, False otherwise.
    """
    x, y = point
    num_vertices = len(polygon)
    inside = False
    j = num_vertices - 1
    for i in range(num_vertices):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# Define the range of possible coordinates for the sheep
x_min, x_max = 50, 1150
y_min, y_max = 50, 750

# Define the parameters for the pathfinder
step_size = 100
x_cg, y_cg = 600, 400

# Initialize the error counter
error_count = 0
Break = False

# Loop 100 times
for i in range(10000):
    # Generate a random arrangement of sheep
    num_sheep = 50
    x_sheep = np.random.uniform(x_min, x_max, num_sheep)
    y_sheep = np.random.uniform(y_min, y_max, num_sheep)
    sheep = np.column_stack((x_sheep, y_sheep))
    x_cg, y_cg = roundup.centroid(sheep)

    # Compute the convex hull
    hull = roundup.GiftWrap.gift_wrapping(sheep)
    hull.append(hull[0])

    # Compute the path
    path = roundup.pathfinder(hull, step_size, x_cg, y_cg)

    # Check if any points in the path are inside the convex hull
    for point in path:
        if is_point_inside_polygon(point, hull) == True:
            error_count += 1
            Break = True
            print(sheep)
            break
        if Break == True:
            break
    if Break == True:
        break



# Print the error count
print(f"Error count: {error_count}")
