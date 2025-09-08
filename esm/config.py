# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import os
from dataclasses import dataclass
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.parent
ESM_DIR = ROOT_DIR / "esm"
FRONTEND_DIR = ROOT_DIR / "frontend"


@dataclass
class Config:
    database_url: str = ""
    port: int = 0
    api_url: str = ""

    def get_default_config(self) -> dict[str, str]:
        port = 8000
        return {
            "database_url": "sqlite:///" + os.path.join(ESM_DIR, "app.db"),
            "port": port,
            "api_url": "http://localhost:{port}",
        }

    def get_config(self) -> dict[str, str]:
        return {
            "database_url": self.database_url,
            "port": self.port,
            "api_url": self.api_url,
        }

    def load_config(self):
        config_path = ESM_DIR / "config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
                self.database_url = config.get("database_url", self.database_url)
                self.port = config.get("port", self.port)
                self.api_url = config.get("api_url", self.api_url)
        else:
            default_config = self.get_default_config()
            self.database_url = default_config["database_url"]
            self.port = default_config["port"]
            self.api_url = default_config["api_url"]

    def save_config(self):
        config_path = ESM_DIR / "config.json"
        with open(config_path, "w") as f:
            json.dump(self.get_config(), f)

    def __str__(self):
        return f"Database URL: {self.database_url}\nPort: {self.port}\nAPI URL: {self.api_url}"
