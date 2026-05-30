# Main.gd — Orchestrates room loading, win/lose flow, and audio.
extends Node2D

const ROOM_COUNT = 3
const BG_COLOR = Color(0.051, 0.031, 0.125)

var _current_room: int = 1
var _player: CharacterBody2D
var _audio: Dictionary = {}
var _overlay: CanvasLayer
var _overlay_label: Label
var _state: String = "playing"


func _ready() -> void:
	_setup_audio()
	_setup_overlay()
	_load_room(_current_room)


func _setup_audio() -> void:
	for sfx_name in ["footstep", "alert", "clear", "caught"]:
		var path = "res://audio/%s.wav" % sfx_name
		if ResourceLoader.exists(path):
			var p = AudioStreamPlayer.new()
			p.stream = load(path)
			p.volume_db = -6.0
			add_child(p)
			_audio[sfx_name] = p


func _setup_overlay() -> void:
	_overlay = CanvasLayer.new()
	_overlay.layer = 10
	add_child(_overlay)
	var bg = ColorRect.new()
	bg.name = "OverlayBG"
	bg.color = Color(0, 0, 0, 0)
	bg.size = Vector2(320, 240)
	_overlay.add_child(bg)
	_overlay_label = Label.new()
	_overlay_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_overlay_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_overlay_label.size = Vector2(320, 240)
	_overlay_label.add_theme_font_size_override("font_size", 14)
	_overlay_label.add_theme_color_override("font_color", Color(0, 1, 1))
	_overlay.add_child(_overlay_label)
	_overlay.visible = false


func _load_room(n: int) -> void:
	for child in get_children():
		if child != _overlay and not _audio.values().has(child):
			child.queue_free()
	await get_tree().process_frame

	var bg = ColorRect.new()
	bg.color = BG_COLOR
	bg.size = Vector2(320, 240)
	add_child(bg)

	var hud = Label.new()
	hud.text = "ROOM %d / %d" % [n, ROOM_COUNT]
	hud.position = Vector2(8, 4)
	hud.add_theme_font_size_override("font_size", 10)
	hud.add_theme_color_override("font_color", Color(0, 1, 1, 0.7))
	add_child(hud)

	var loader = load("res://scripts/RoomLoader.gd").new()
	add_child(loader)
	var room_data: Dictionary = loader.load_room("res://rooms/room_%d.tmj" % n, self)

	# Build sprite before add_child so _sprite ref is valid from frame 1
	var sprite = Sprite2D.new()
	sprite.name = "Sprite2D"
	if ResourceLoader.exists("res://sprites/android_ss.png"):
		sprite.texture = load("res://sprites/android_ss.png")
		sprite.hframes = 8
		sprite.vframes = 1
		sprite.frame = 0
	else:
		var img = Image.create(16, 16, false, Image.FORMAT_RGB8)
		img.fill(Color(0, 1, 1))
		sprite.texture = ImageTexture.create_from_image(img)

	_player = CharacterBody2D.new()
	_player.set_script(load("res://scripts/Player.gd"))
	_player.name = "Player"
	_player.add_to_group("player")
	_player.add_child(sprite)
	_player._sprite = sprite
	add_child(_player)
	_player.global_position = room_data["player_start"]
	_player.exit_rect = room_data["exit_rect"]
	if _audio.has("footstep"):
		_player.setup_audio(_audio["footstep"])
	_player.reached_exit.connect(_on_reached_exit)

	for drone_info in room_data["drone_data"]:
		_spawn_drone(drone_info)

	_state = "playing"
	_overlay.visible = false


func _spawn_drone(info: Dictionary) -> void:
	var drone = Area2D.new()
	drone.set_script(load("res://scripts/Drone.gd"))
	var cone = Polygon2D.new()
	cone.name = "LightCone"
	drone.add_child(cone)
	var dspr = Sprite2D.new()
	dspr.name = "Sprite2D"
	if ResourceLoader.exists("res://sprites/drone.png"):
		dspr.texture = load("res://sprites/drone.png")
	else:
		var img = Image.create(16, 16, false, Image.FORMAT_RGB8)
		img.fill(Color(1, 0.13, 0.27))
		dspr.texture = ImageTexture.create_from_image(img)
	drone.add_child(dspr)
	add_child(drone)
	drone.setup(info["position"], info["patrol"])
	drone.set_physics_process(true)
	drone.player_spotted.connect(_on_caught)


func _on_caught() -> void:
	if _state != "playing": return
	_state = "caught"
	if _audio.has("caught"): _audio["caught"].play()
	_show_overlay("UNIT 7 RETIRED\n\n[TAP TO RESTART]", Color(1, 0.13, 0.27))


func _on_reached_exit() -> void:
	if _state != "playing": return
	if _audio.has("clear"): _audio["clear"].play()
	if _current_room < ROOM_COUNT:
		_state = "clear"
		_current_room += 1
		_show_overlay("SECTOR CLEAR\n\nPROCEEDING...", Color(0, 1, 1))
		await get_tree().create_timer(1.5).timeout
		_load_room(_current_room)
	else:
		_state = "complete"
		_show_overlay(
			"GHOST PROTOCOL COMPLETE\n\n\"Do I dream? I'll find out.\"\n\n[TAP TO RESTART]",
			Color(0, 1, 1)
		)


func _show_overlay(text: String, color: Color) -> void:
	_overlay.get_node("OverlayBG").color = Color(0, 0, 0, 0.75)
	_overlay_label.text = text
	_overlay_label.add_theme_color_override("font_color", color)
	_overlay.visible = true


func _input(event: InputEvent) -> void:
	if _state not in ["caught", "complete"]: return
	if event is InputEventKey and event.pressed and not event.echo:
		_current_room = 1; _load_room(1)
	if event is InputEventScreenTouch and event.pressed:
		_current_room = 1; _load_room(1)
