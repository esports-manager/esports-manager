# Testing Logic

The purpose of this document is to explain and brainstorm the testing of the main features of the game.

## Match Live

The match live feature is the game's main feature: it calculates how a match plays out based on all the variables
of the given eSport, and prints everything that happens in the simulated game to the user.

Right now the priority is to implement the Match Live feature for a MOBA game, using League of Legends as a starting
point. In the future, the idea is that the user may implement his own MOBA game, and since these games share many
characteristics, he can play around with the functions that are implemented in the match live calculation.

As of now, the only thing it will do is use probability calculations using player's skills and each champion's skills
to produce fictional results. This means that you will not be able to see any action on screen, just read it like
someone is transcribing what the Narrator is saying. We might implement some graphical and sound elements to make it more
interesting in events such as a First Blood, a Quadrakill or Pentakill, slaying Baron or Dragon and winning or losing the
game.

In the future we might implement some form of graphical interaction, seeing each champion move on the map and actually
simulate everything that happens on the Rift, but this is not a priority, and it will take a lot longer to implement
than a simple text-like function.

## How will it work

The match is simulated using an object that is declared from the Match class. The Match class holds all the methods
used to simulate the match. The match simulation starts using the `Match.match_live()` method.

The match object receives the 2 teams, and the parameters that tell the `match_live()` whether it should output
commentary and the speed of the simulation, as well as the frequency of the commentary output (not yet implemented).

So the game starts with a time counter, that uses Python's `time` module. We get the current system time,
storing it on `start_time` and calculate how much time has passed since the game started, using the
`Match.elapsed_time` variable. The `Match.match_speed` parameter uses the `elapsed_time` value to calculate
when it should start calculating each match event, and that gets translated into a `game_time` value, that outputs
the current duration of the game and the time that each event happened.

The `game_time` determines when things should start happening, and increases the probability of ending the game.

From 0 to 3 minutes, the game might have an initial team fight, teams might decide for an invade, depending on
each team's stats. The outcome of this team fight is determined by the `Match.event_team_fight()` method, that
receives a list with the players involved in the team fight and calculates the outcome of the team fight.
Players might also decide to do nothing, which is much more common, and the game starts without much fuzz.

If no team fight has happened in the initial minutes, the game moves on to the early game phase, the laning
phase. Each tick of time will calculate the probability of players going to gank lanes or deciding on aggression.
For at least 10 `game_time` minutes, no tower_taking event will be considered, as it is too early for that
to happen. After that mark, the game will start increasing the probability of a tower being taken, and
team fights will happen more frequently.

The events considering taking barracks/inhibitors will only be considered after every tower from one lane is taken.
