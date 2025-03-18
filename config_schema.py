"""Configuration schema for the Float Cards addon."""

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "window_width": {
            "type": "integer",
            "minimum": 100,
            "maximum": 2000,
            "default": 400
        },
        "window_height": {
            "type": "integer",
            "minimum": 100,
            "maximum": 2000,
            "default": 300
        },
        "button_height": {
            "type": "integer",
            "minimum": 10,
            "maximum": 100,
            "default": 20
        },
        "shortcut": {
            "type": "string",
            "default": "Ctrl+Alt+P"
        },
        "position_x": {
            "type": "integer",
            "default": 0
        },
        "position_y": {
            "type": "integer",
            "default": 0
        },
        "stay_on_top": {
            "type": "boolean",
            "default": True
        },
        "buttons": {
            "type": "object",
            "properties": {
                "again": {"type": "boolean", "default": True},
                "hard": {"type": "boolean", "default": True},
                "good": {"type": "boolean", "default": True},
                "easy": {"type": "boolean", "default": True}
            },
            "additionalProperties": False
        },
        "hotkeys": {
            "type": "object",
            "properties": {
                "toggle_stay_on_top": {"type": "string", "default": "Ctrl+T"},
                "replay_sound": {"type": "string", "default": "R"},
                "replay_second_sound": {"type": "string", "default": "Ctrl+R"},
                "toggle_scheduling": {"type": "string", "default": "Ctrl+Alt+S"},
                "toggle_auto_close": {"type": "string", "default": "Ctrl+Alt+A"}
            },
            "additionalProperties": False
        },
        "theme": {
            "type": "object",
            "properties": {
                "light": {
                    "type": "object",
                    "properties": {
                        "background": {"type": "string", "default": "#FFFFFF"},
                        "text": {"type": "string", "default": "#000000"}
                    }
                },
                "dark": {
                    "type": "object",
                    "properties": {
                        "background": {"type": "string", "default": "#2F2F31"},
                        "text": {"type": "string", "default": "#FFFFFF"}
                    }
                }
            },
            "additionalProperties": False
        },
        "scheduling": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "frequency": {"type": "integer", "minimum": 1, "maximum": 1440, "default": 1},
                "deck": {"type": "string", "default": "Default"}
            }
        }
    },
    "additionalProperties": False,
    "required": [
        "window_width",
        "window_height",
        "button_height",
        "shortcut",
        "position_x",
        "position_y",
        "stay_on_top",
        "buttons",
        "hotkeys",
        "theme",
        "scheduling"
    ]
} 