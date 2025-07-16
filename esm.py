#  eSports Manager - free and open source eSports Management game
#  Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import webview
import uvicorn
import threading
from esm import create_api
from frontend import create_frontend


def get_app():
    app = create_api()
    app = create_frontend(app)
    return app


def start_server():
    app = get_app()
    uvicorn.run(app, host="0.0.0.0", port=8125, log_level="info")


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    webview.create_window(
        "eSports Manager",
        "http://localhost:8125/",
        width=1200,
        height=800,
        resizable=True,
    )
    webview.start(icon="frontend/static/img/trophy.svg", gui="qt")
