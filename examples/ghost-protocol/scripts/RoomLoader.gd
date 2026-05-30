# RoomLoader.gd
# Parses a Tiled .tmj file and builds the room into the parent node.
# Tile values: 0=empty, 1=floor, 2=wall
# Returns dict: {player_start: Vector2, exit_rect: Rect2, drone_data: Array}
extends Node

const TILE_SIZE = 16
const FLOOR_COLOR = Color(0.1, 0.06, 0.19)
const WALL_COLOR  = Color(0.04, 0.06, 0.1)

var _parent: Node


func load_room(tmj_path: String, parent: Node) -> Dictionary:
	_parent = parent
	var file = FileAccess.open(tmj_path, FileAccess.READ)
	if not file:
		push_error("RoomLoader: cannot open " + tmj_path)
		return {}
	var map: Dictionary = JSON.parse_string(file.get_as_text())
	file.close()

	var floor_data: Array = []
	var wall_data: Array = []
	var objects: Array = []
	var map_w: int = map["width"]

	for layer in map["layers"]:
		match layer["name"]:
			"floor":   floor_data = layer["data"]
			"walls":   wall_data  = layer["data"]
			"objects": objects    = layer["objects"]

	_build_tiles(floor_data, wall_data, map_w)
	return _extract_objects(objects)


func _build_tiles(floor_data: Array, wall_data: Array, map_w: int) -> void:
	for i in range(floor_data.size()):
		var tx = i % map_w
		var ty = i / map_w
		var px = tx * TILE_SIZE
		var py = ty * TILE_SIZE
		if floor_data[i] != 0:
			_add_rect(px, py, FLOOR_COLOR)
		if wall_data[i] != 0:
			_add_rect(px, py, WALL_COLOR)
			_add_wall_collision(px, py)


func _add_rect(px: int, py: int, color: Color) -> void:
	var rect = ColorRect.new()
	rect.position = Vector2(px, py)
	rect.size = Vector2(TILE_SIZE, TILE_SIZE)
	rect.color = color
	_parent.add_child(rect)


func _add_wall_collision(px: int, py: int) -> void:
	var body = StaticBody2D.new()
	body.position = Vector2(px + TILE_SIZE / 2, py + TILE_SIZE / 2)
	var shape = CollisionShape2D.new()
	var rect_shape = RectangleShape2D.new()
	rect_shape.size = Vector2(TILE_SIZE, TILE_SIZE)
	shape.shape = rect_shape
	body.add_child(shape)
	body.collision_layer = 1
	body.collision_mask = 0
	_parent.add_child(body)


func _extract_objects(objects: Array) -> Dictionary:
	var result = {"player_start": Vector2.ZERO, "exit_rect": Rect2(), "drone_data": []}
	for obj in objects:
		var name: String = obj["name"]
		if name == "player_start":
			result["player_start"] = Vector2(obj["x"], obj["y"])
		elif name == "exit":
			result["exit_rect"] = Rect2(obj["x"], obj["y"], obj["width"], obj["height"])
		elif name.begins_with("drone_"):
			var patrol: Array = JSON.parse_string(_get_prop(obj, "patrol_path", "[]"))
			result["drone_data"].append({
				"position": Vector2(obj["x"], obj["y"]),
				"patrol": patrol.map(func(wp): return Vector2(wp[0], wp[1])),
			})
	return result


func _get_prop(obj: Dictionary, prop_name: String, default: String) -> String:
	if not obj.has("properties"):
		return default
	for prop in obj["properties"]:
		if prop["name"] == prop_name:
			return prop["value"]
	return default
