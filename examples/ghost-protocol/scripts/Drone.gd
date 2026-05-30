# Drone.gd
# Area2D that patrols between waypoints and sweeps a triangular light cone.
# Emits player_spotted when the player's CharacterBody2D enters its cone area.
# Collision: layer=4, mask=2 (detects player on layer 2).
extends Area2D

signal player_spotted

const SPEED = 40.0
const CONE_LENGTH = 80.0
const CONE_HALF_ANGLE = 0.52  # ~30 deg each side = 60 deg FOV

var patrol_path: Array = []
var _target_index: int = 1
var _alerting: bool = false
var _alert_timer: float = 0.0

@onready var _cone: Polygon2D = $LightCone


func _ready() -> void:
	var shape_node = CollisionShape2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 7.0
	shape_node.shape = circle
	add_child(shape_node)
	collision_layer = 4
	collision_mask = 2
	connect("body_entered", _on_body_entered)
	_update_cone()


func setup(pos: Vector2, waypoints: Array) -> void:
	global_position = pos
	patrol_path = waypoints if waypoints.size() >= 2 else [pos, pos]


func _physics_process(delta: float) -> void:
	if _alerting:
		_alert_timer -= delta
		if _alert_timer <= 0:
			_alerting = false
			if _cone: _cone.color = Color(1.0, 0.84, 0.0, 0.3)
		return

	if patrol_path.size() < 2:
		return

	var target = patrol_path[_target_index]
	var to_target = target - global_position
	if to_target.length() < 2.0:
		_target_index = (_target_index + 1) % patrol_path.size()
		return

	var dir = to_target.normalized()
	global_position += dir * SPEED * delta
	rotation = dir.angle()
	_update_cone()


func _update_cone() -> void:
	if not _cone:
		return
	var l = Vector2(cos(-CONE_HALF_ANGLE), sin(-CONE_HALF_ANGLE)) * CONE_LENGTH
	var r = Vector2(cos(CONE_HALF_ANGLE),  sin(CONE_HALF_ANGLE))  * CONE_LENGTH
	_cone.polygon = PackedVector2Array([Vector2.ZERO, l, r])
	if not _alerting:
		_cone.color = Color(1.0, 0.84, 0.0, 0.3)


func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player") and not _alerting:
		_alerting = true
		_alert_timer = 0.5
		if _cone: _cone.color = Color(1.0, 0.13, 0.27, 0.5)
		player_spotted.emit()
