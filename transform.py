import math
import pygame as pg
import boids

REFERENCE_COORD = pg.Vector2(51.6206761736925, -2.514666327940187)

EARTH_CIRC = 40075e3 # km
M_PER_LAT = EARTH_CIRC / 360 # meters per degree of latitude
M_PER_LNG = EARTH_CIRC * math.cos(REFERENCE_COORD.x / 180 * math.pi) / 360 # using x because latitude is upwards

PIX_PER_METER = 15
WINDOW_HEIGHT = 800

def TransformLP(lat_long):
    rel_lat_long = lat_long - REFERENCE_COORD

    return pg.Vector2(
        rel_lat_long.y * M_PER_LNG * PIX_PER_METER,
        WINDOW_HEIGHT - rel_lat_long.x * M_PER_LAT * PIX_PER_METER # Flipping becaue (0,0) is top left in pg
    ) # switching x and y because lat and long are (y,x)

def TransformPL(pix_point):
    return pg.Vector2(
        (WINDOW_HEIGHT - pix_point.y) / (M_PER_LAT * PIX_PER_METER),
        pix_point.x / (M_PER_LNG * PIX_PER_METER) # Flipping becaue (0,0) is top left in pg
    ) + REFERENCE_COORD



def GetWallBounds(wall_JSON):
    min_point = pg.Vector2(
        wall_JSON[0]["points"][0][0],
        wall_JSON[0]["points"][0][1]
    )
    max_point = pg.Vector2(
        wall_JSON[0]["points"][0][0],
        wall_JSON[0]["points"][0][1]
    )

    for wall in wall_JSON:
        for point in wall["points"]:
            min_point.x = min(min_point.x, point[0])
            max_point.x = max(max_point.x, point[0])
            min_point.y = min(min_point.y, point[1])
            max_point.y = max(max_point.y, point[1])

    return {
        "min": min_point,
        "max": max_point
    }
