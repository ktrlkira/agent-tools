# Player.gd
# Top-down CharacterBody2D. WASD/Arrow movement at 80px/s.
# _sprite is set by Main.gd before add_child so it is available from frame 1.
# Emits reached_exit when overlapping exit_rect.
extends CharacterBody2D

signal reached_exit

const SPEED = 80.0

var exit_rect: Rect2 = Rect2()
var _sprite: Sprite2D
var _footstep_sound: AudioStreamPlayer
var _footstep_timer: float = 0.0
var _dir_index: int = 0   # 0=S 1=N 2=E 3=W
var _walk_frame: int = 0
var _anim_timer: float = 0.0


func _ready() -> void:
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(8, 12)
	shape.shape = rect
	add_child(shape)
	collision_layer = 2
	collision_mask = 1


func _physics_process(delta: float) -> void:
	var dir = Vector2.ZERO
	if Input.is_action_pressed("ui_right"):  dir.x += 1; _dir_index = 2
	if Input.is_action_pressed("ui_left"):   dir.x -= 1; _dir_index = 3
	if Input.is_action_pressed("ui_down"):   dir.y += 1; _dir_index = 0
	if Input.is_action_pressed("ui_up"):     dir.y -= 1; _dir_index = 1

	if dir != Vector2.ZERO:
		dir = dir.normalized()
		_anim_timer += delta
		if _anim_timer >= 0.15:
			_anim_timer = 0.0
			_walk_frame = 1 - _walk_frame
		_footstep_timer += delta
		if _footstep_timer >= 0.25 and _footstep_sound:
			_footstep_timer = 0.0
			_footstep_sound.play()
	else:
		_walk_frame = 0

	if _sprite:
		_sprite.frame = _dir_index * 2 + _walk_frame

	velocity = dir * SPEED
	move_and_slide()

	if exit_rect != Rect2() and exit_rect.has_point(global_position):
		reached_exit.emit()


func setup_audio(footstep: AudioStreamPlayer) -> void:
	_footstep_sound = footstep
