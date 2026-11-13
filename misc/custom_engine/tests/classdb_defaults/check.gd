extends SceneTree


func _initialize() -> void:
	# These extension classes have required getters, but supply explicit defaults
	# so documentation/default discovery does not have to call those getters.
	assert(ClassDB.class_get_property_default_value("MultiplayerPeerExtension", "transfer_mode") == MultiplayerPeer.TRANSFER_MODE_RELIABLE)
	assert(ClassDB.class_get_property_default_value("MultiplayerPeerExtension", "transfer_channel") == 0)
	assert(ClassDB.class_get_property_default_value("WebRTCDataChannelExtension", "write_mode") == WebRTCDataChannel.WRITE_MODE_BINARY)
	# Defaults not explicitly supplied must still be discovered from the object.
	assert(ClassDB.class_get_property_default_value("Node3D", "position") == Vector3.ZERO)
	assert(ClassDB.class_get_property_default_value("Node3D", "visible") == true)
	# Repeated queries must use the completed cache without changing the values.
	assert(ClassDB.class_get_property_default_value("MultiplayerPeerExtension", "transfer_channel") == 0)
	print("CLASSDB_EXPLICIT_DEFAULTS_PASS")
	quit(0)
