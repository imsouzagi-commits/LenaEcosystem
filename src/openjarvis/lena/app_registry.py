from __future__ import annotations


class LenaAppRegistry:
    APP_NAME_MAP = {
        "safari": "Safari",
        "spotify": "Spotify",
        "finder": "Finder",
        "terminal": "Terminal",
        "prompt": "Terminal",
        "console": "Terminal",
        "shell": "Terminal",
        "notes": "Notes",
        "notas": "Notes",
        "calendar": "Calendar",
        "calculator": "Calculator",
        "music": "Music",
        "photos": "Photos",
        "mail": "Mail",
        "maps": "Maps",
        "preview": "Preview",
        "textedit": "TextEdit",
        "dictionary": "Dictionary",
        "chess": "Chess",
        "tv": "TV",
        "reminders": "Reminders",
        "facetime": "FaceTime",
        "app store": "App Store",
        "system settings": "System Settings",
        "ajustes do sistema": "System Settings",
        "configurações": "System Settings",
        "configuracoes": "System Settings",
        "preferências do sistema": "System Settings",
        "preferences": "System Settings",

        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "google": "Google Chrome",
        "navegador": "Google Chrome",

        "atlas": "ChatGPT Atlas",
        "atlas gpt": "ChatGPT Atlas",
        "atlasgpt": "ChatGPT Atlas",
        "gpt atlas": "ChatGPT Atlas",
        "chatgpt atlas": "ChatGPT Atlas",

        "chatgpt": "ChatGPT",
        "chat gpt": "ChatGPT",
    }

    APP_PATH_MAP = {
        "ChatGPT Atlas": "/Applications/ChatGPT Atlas.app",
        "ChatGPT": "/Applications/ChatGPT.app",
        "Google Chrome": "/Applications/Google Chrome.app",
        "Terminal": "/System/Applications/Utilities/Terminal.app",
        "System Settings": "/System/Applications/System Settings.app",
    }

    APP_PROCESS_HINTS = {
        "Spotify": ["Spotify"],
        "Safari": ["Safari"],
        "Finder": ["Finder"],
        "Terminal": ["Terminal"],
        "Notes": ["Notes"],
        "Google Chrome": ["Google Chrome", "Google Chrome Helper", "/Applications/Google Chrome.app"],
        "ChatGPT": ["ChatGPT", "ChatGPTHelper", "/Applications/ChatGPT.app"],
        "ChatGPT Atlas": [
            "ChatGPT Atlas",
            "ChatGPT Atlas Helper",
            "/Applications/ChatGPT Atlas.app",
            "com.openai.atlas",
        ],
    }
