**NOTE:** *THIS PROJECT IS STILL UNDER DEVELOPMENT, AND IS NOT READY FOR GAMEPLAY YET. AS SOON AS GAMEPLAY FEATURES ARE IMPLEMENTED, THIS NOTE WILL BE REMOVED AND NEW INFO WILL BE ADDED TO THIS REPOSITORY.*

![eSports Manager Logo](src/resources/images/logo/esportsmanager.png)

# eSports Manager

**eSports Manager** aims to become a free and open source eSports management game, licensed under the [GPLv3](LICENSE.md), based on titles like Football Manager and the deceased Championship Manager.

The idea here is to bring a full-fledged experience in eSports, playing major leagues and big championships, managing players, setting up practices and discovering new talents.

In this game, you will be able set up your team, get them to play in whatever position you would like them to, set up strategies, choose which race/champion/hero they're going to play with, and read match descriptions as they happen live, much like Football Manager on its early days. Managing finances, finding sponsors, boosting your players' morale are also going to play a role in that experience.

## INSTALLATION

The game is still not ready to be played. Many features are yet to be implemented, and a lot of things are missing. There's no gameplay experience, only testing material here.

## HOW TO RUN THE DEBUG VERSION

To run the debug version first you need to have Python 3 installed. Probably this game should work with Python 3.8+, I don't know if it works with Python 3.6 or lower, but from what I remember, some functions that I use were only implemented in 3.8. Currently testing on 3.9 and it is working.

To manage dependencies, we use Pipenv. To install pipenv:

```
pip install pipenv
```

Then, clone the repo and run:

```
pipenv install
```

And then you can do:

```
pipenv shell
```

To get into the python virtual environment shell. And then just run:

```
python esm.py
```

And that should run the basic Debug Match Window. There's very limited functionality here, Match Simulation is still under development, but you can see basically what events would happen in your match.

If you want to generate a number X of players, edit the `esm.py` file and change the `num_players` variable to a number that's at max 3500.

I haven't tested with a number of players that's not divisible by 5, and that should not work, so try to choose numbers that are divisible by 5. We can fix that later.

## FEATURES

Check [FEATURES.md](FEATURES.md) to get more information on the planned features and features that are already implemented.

## CONTRIBUTE

Check our [CONTRIBUTING.md](CONTRIBUTING.md) to get more information on how to contribute to the project.

## LICENSE

    eSports Manager - A free and open source eSports management game
    Copyright (C) 2020  Pedrenrique G. Guimarães

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Check [LICENSE](LICENSE.md) for more information.
