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
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_game")
def new_game():
    return render_template("layout.html")


@app.route("/load_game")
def load_game():
    return "<p>load game</p>"


@app.route("/debug_mode")
def debug_mode():
    return "<p>debug mode</p>"


@app.route("/settings")
def settings():
    return "<p>settings</p>"


if __name__ == "__main__":
    app.run(debug=True)
