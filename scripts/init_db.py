# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session
from esm.db import DatabaseManager
from esm.config import Config
from esm.models.tournament import (
    Tournament,
    TournamentType,
    TournamentFormat,
    TournamentTier,
)
from esm.models.moba.team import MobaTeam
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionRole,
    MobaChampionType,
    MobaChampionDifficulty,
)
from esm.models.moba.player_contract import MobaPlayerContract


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return []


def import_tournaments(session: Session, data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Import tournament data into the database."""
    print("Importing tournaments...")
    tournament_map = {}  # Map tournament names to IDs

    for item in data:
        start_date = (
            datetime.strptime(item["start_date"], "%Y-%m-%d")
            if item.get("start_date")
            else None
        )
        end_date = (
            datetime.strptime(item["end_date"], "%Y-%m-%d")
            if item.get("end_date")
            else None
        )

        tournament = Tournament(
            name=item["name"],
            abbreviation=item.get("abbreviation"),
            type=TournamentType(item["type"]),
            format=TournamentFormat(item["format"]),
            tier=TournamentTier(item["tier"]),
            start_date=start_date,
            end_date=end_date,
            location=item.get("location"),
            description=item.get("description"),
            default_color=item.get("default_color"),
            logo_path=item.get("logo_path"),
        )

        session.add(tournament)
        session.flush()  # Flush to get the ID
        tournament_map[item["name"]] = tournament.id
        print(f"  Added tournament: {item['name']}")

    session.commit()
    print(f"Imported {len(tournament_map)} tournaments")
    return tournament_map


def import_teams(session: Session, data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Import team data into the database."""
    print("Importing teams...")
    team_map = {}  # Map team names to IDs

    for item in data:
        team = MobaTeam(
            name=item["name"],
            nationality=item.get("nationality"),
            region=item.get("region"),
            description=item.get("description"),
            logo_path=item.get("logo_path"),
            banner_path=item.get("banner_path"),
        )

        session.add(team)
        session.flush()  # Flush to get the ID
        team_map[item["name"]] = team.id
        print(f"  Added team: {item['name']}")

    session.commit()
    print(f"Imported {len(team_map)} teams")
    return team_map


def import_champions(session: Session, data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Import champion data into the database."""
    print("Importing champions...")
    champion_map = {}  # Map champion names to IDs

    for item in data:
        release_date = datetime.strptime(item["release_date"], "%Y-%m-%d").date()

        secondary_role = (
            MobaChampionRole(item["secondary_role"])
            if item.get("secondary_role")
            else None
        )
        champion_type2 = (
            MobaChampionType(item["champion_type2"])
            if item.get("champion_type2")
            else None
        )

        champion = MobaChampion(
            name=item["name"],
            release_date=release_date,
            primary_role=MobaChampionRole(item["primary_role"]),
            secondary_role=secondary_role,
            champion_type1=MobaChampionType(item["champion_type1"]),
            champion_type2=champion_type2,
            difficulty=MobaChampionDifficulty(item["difficulty"]),
            strength=item["strength"],
            image_path=item.get("image_path"),
            description=item.get("description"),
            win_rate=item.get("win_rate"),
            pick_rate=item.get("pick_rate"),
            ban_rate=item.get("ban_rate"),
        )

        session.add(champion)
        session.flush()  # Flush to get the ID
        champion_map[item["name"]] = champion.id
        print(f"  Added champion: {item['name']}")

    session.commit()
    print(f"Imported {len(champion_map)} champions")
    return champion_map


def import_players(
    session: Session,
    data: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Import player data into the database."""
    print("Importing players...")
    player_map = {}  # Map player nicknames to IDs

    for item in data:
        date_of_birth = datetime.strptime(item["date_of_birth"], "%Y-%m-%d").date()

        player = MobaPlayer(
            first_name=item["first_name"],
            last_name=item["last_name"],
            nick_name=item["nick_name"],
            date_of_birth=date_of_birth,
            nationality=item.get("nationality"),
            bio=item.get("bio"),
            image_path=item.get("image_path"),
            role=MobaPlayerRole(item["role"]),
            is_active=item.get("is_active", True),
            mechanics=item.get("mechanics", 50),
            knowledge=item.get("knowledge", 50),
            agility=item.get("agility", 50),
            reflexes=item.get("reflexes", 50),
            accuracy=item.get("accuracy", 50),
            aggression=item.get("aggression", 50),
            vision=item.get("vision", 50),
            farming=item.get("farming", 50),
            communication=item.get("communication", 50),
            concentration=item.get("concentration", 50),
            leadership=item.get("leadership", 50),
            teamwork=item.get("teamwork", 50),
            decisions=item.get("decisions", 50),
            morale=item.get("morale", 50),
            form=item.get("form", 50),
            value=item.get("value", 1000000),
        )

        session.add(player)
        session.flush()  # Flush to get the ID
        player_map[item["nick_name"]] = player.id
        print(f"  Added player: {item['nick_name']}")

    session.commit()
    print(f"Imported {len(player_map)} players")
    return player_map


def create_player_contracts(
    session: Session,
    player_map: Dict[str, int],
    team_map: Dict[str, int],
) -> None:
    """Create player contracts based on the team information in players data."""
    print("Creating player contracts...")
    contracts_created = 0

    for i in range(len(player_map), 5):
        team_index = i // 5
        players = [
            player_map[i],
            player_map[i + 1],
            player_map[i + 2],
            player_map[i + 3],
            player_map[i + 4],
        ]
        player_ids = [player[0] for player in players]

        for player_id in player_ids:
            contract = MobaPlayerContract(
                player_id=player_id,
                team_id=team_map[team_index],
                start_date=datetime.now().date(),
                end_date=datetime(2026, 12, 31).date(),
                salary=500000,
                is_active=True,
            )

            session.add(contract)
            session.commit()
            contracts_created += 1
            print(f"  Created contract: {player_id} -> {team_map[team_index]}")

    session.flush()
    print(f"Created {contracts_created} player contracts")


def main():
    """Main function to import all data."""
    print("Starting data import...")

    config = Config()
    config.load_config()

    db_manager = DatabaseManager(config.database_url)

    script_dir = Path(__file__).parent

    tournaments_file = script_dir / "tournaments.json"
    teams_file = script_dir / "teams.json"
    players_file = script_dir / "players.json"
    champions_file = script_dir / "champions.json"

    for file_path in [tournaments_file, teams_file, players_file, champions_file]:
        if not file_path.exists():
            print(f"Error: {file_path} does not exist")
            return

    tournaments_data = load_json_file(tournaments_file)
    teams_data = load_json_file(teams_file)
    players_data = load_json_file(players_file)
    champions_data = load_json_file(champions_file)

    # Import data into the database
    with Session(db_manager.engine) as session:
        # Import data in order of dependencies
        import_tournaments(session, tournaments_data)
        team_map = import_teams(session, teams_data)
        import_champions(session, champions_data)
        player_map = import_players(session, players_data)

        # Create player contracts
        create_player_contracts(session, player_map, team_map)

    print("Data import completed successfully!")


if __name__ == "__main__":
    main()
