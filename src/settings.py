from json import load, dump
from utils import convert_vals


class Settings:
    def __init__(self, fn):
        self.fn = fn
        self.settings = {}
        try:
            self.load_settings()
        except Exception:
            self.set("created", True)

    def load_settings(self):
        with open(self.fn, "r") as f:
            self.settings = load(f)

    def set(self, k, v):
        self.settings[k] = v
        with open(self.fn, "w") as f:
            dump(self.settings, f)

    def get(self, k, fallback=None):
        try:
            return self.settings[k]
        except KeyError:
            if fallback:
                self.set(k, fallback)
                return fallback
            else:
                raise KeyError("No such setting: {}".format(k))


settings = Settings("settings.json")


class SettingsListAPI:
    def __init__(self, settings):
        self._settings = settings

    def get(self, data):
        return settings.settings


class SettingsAPI:
    def __init__(self, settings):
        self._settings = settings

    def get(self, data, setting):
        if setting not in self._settings.settings:
            return {"error": f"No such setting {setting}"}, 400

        return {"value": self._settings.get(setting)}

    def put(self, data, setting):
        try:
            val = convert_vals(data["value"])
            settings.set(setting, val)
            return {"message": "success"}
        except Exception as e:
            return {"error": str(e)}, 400


api = {
    "settings": SettingsListAPI(settings),
    "settings/<setting>": SettingsAPI(settings),
}
