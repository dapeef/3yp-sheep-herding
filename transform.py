import math
import pygame as pg

class Transform():
    def __init__(self, bounds, pix_per_meter, window_height):
        self.bounds = bounds
        self.pix_per_meter = pix_per_meter
        self.window_height = window_height

    def TransformLP(self, lat_long):
        bound_center = (self.bounds["min"] + self.bounds["max"]) / 2

        earth_circ = 40075e3 # km
        m_per_lat = earth_circ / 360 # meters per degree of latitude
        m_per_lng = earth_circ * math.cos(bound_center.y / 180 * math.pi) / 360

        rel_lat_long = lat_long - pg.Vector2(self.bounds["min"])

        return pg.Vector2(
            rel_lat_long.y * m_per_lng * self.pix_per_meter,
            self.window_height - rel_lat_long.x * m_per_lat * self.pix_per_meter # Flipping becaue (0,0) is top left in pg
        ) # switching x and y because lat and long are (y,x)


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


if __name__ == "__main__":
    import json

    # with open("infrastructure-data.json") as f:
    #     print(LatLongToPix(json.load(f)["walls"][:5]))