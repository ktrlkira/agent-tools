#!/usr/bin/env python3
"""Generates Ghost Protocol Tiled room maps (.tmj) for 3 rooms."""
import json, os

W, H, TS = 20, 15, 16
EMPTY, FLOOR, WALL = 0, 1, 2


def flat(grid): return [c for row in grid for c in row]

def tile_layer(name, grid, lid):
    return {"data": flat(grid), "height": H, "id": lid, "name": name,
            "opacity": 1, "type": "tilelayer", "visible": True, "width": W, "x": 0, "y": 0}

def obj_layer(name, objects, lid):
    return {"draworder": "topdown", "id": lid, "name": name, "objects": objects,
            "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0}

def pt(oid, name, tx, ty, props=None):
    o = {"id": oid, "name": name, "point": True, "type": "",
         "x": tx*TS, "y": ty*TS, "width": 0, "height": 0}
    if props: o["properties"] = props
    return o

def rect(oid, name, tx, ty, tw=2, th=2):
    return {"id": oid, "name": name, "type": "", "point": False,
            "x": tx*TS, "y": ty*TS, "width": tw*TS, "height": th*TS}

def patrol(waypoints):
    return {"name": "patrol_path", "type": "string",
            "value": json.dumps([[x*TS, y*TS] for x, y in waypoints])}

def make_walls(extras=None):
    extras = extras or set()
    return [[WALL if (x==0 or x==W-1 or y==0 or y==H-1 or (x,y) in extras) else EMPTY
             for x in range(W)] for y in range(H)]

def make_floor(walls):
    return [[FLOOR if walls[y][x]==EMPTY else EMPTY for x in range(W)] for y in range(H)]

def make_map(floor, walls, objects):
    return {
        "compressionlevel": -1, "height": H, "infinite": False,
        "layers": [tile_layer("floor", floor, 1), tile_layer("walls", walls, 2),
                   obj_layer("objects", objects, 3)],
        "nextlayerid": 4, "nextobjectid": 20,
        "orientation": "orthogonal", "renderorder": "right-down",
        "tiledversion": "1.12.2", "tileheight": TS, "tilewidth": TS,
        "tilesets": [], "type": "map", "version": "1.12", "width": W,
    }


# Room 1 — Intake Bay: wide open, 1 slow drone
r1w = make_walls({(4,4),(5,4),(6,4),(13,10),(14,10),(15,10)})
ROOM_1 = make_map(make_floor(r1w), r1w, [
    pt(1, "player_start", 1, 1),
    rect(2, "exit", 17, 12),
    pt(3, "drone_1", 4, 7, [patrol([(4,7),(15,7)])]),
])

# Room 2 — Processing Corridor: 2 drones, crossing paths
r2w = make_walls({(3,5),(4,5),(5,5),(6,5),(7,5),(12,9),(13,9),(14,9),(15,9),(16,9),
                  (9,3),(9,4),(9,5),(9,6),(10,8),(10,9),(10,10),(10,11)})
ROOM_2 = make_map(make_floor(r2w), r2w, [
    pt(1, "player_start", 1, 1),
    rect(2, "exit", 17, 12),
    pt(3, "drone_1", 3, 3, [patrol([(3,3),(16,3)])]),
    pt(4, "drone_2", 15, 5, [patrol([(15,5),(15,12)])]),
])

# Room 3 — Launch Control: 3 drones, tight routing
r3w = make_walls({(3,3),(4,3),(5,3),(3,4),(3,5),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),
                  (16,4),(16,5),(16,6),(16,7),(16,8),(3,10),(4,10),(5,10),(3,11),(4,11),
                  (11,10),(12,10),(13,10)})
ROOM_3 = make_map(make_floor(r3w), r3w, [
    pt(1, "player_start", 1, 1),
    rect(2, "exit", 17, 12),
    pt(3, "drone_1", 8, 2, [patrol([(8,2),(14,2)])]),
    pt(4, "drone_2", 6, 7, [patrol([(6,7),(6,13)])]),
    pt(5, "drone_3", 14, 11, [patrol([(14,11),(8,11)])]),
])

out = os.path.expanduser("~/ghost-protocol/rooms")
os.makedirs(out, exist_ok=True)
for name, data in [("room_1", ROOM_1), ("room_2", ROOM_2), ("room_3", ROOM_3)]:
    path = os.path.join(out, f"{name}.tmj")
    with open(path, 'w') as f: json.dump(data, f, indent=2)
    print(f"  wrote {path}")
