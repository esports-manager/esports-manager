#!/bin/bash

# Base URL
BASE_URL="http://localhost:8000/api/moba/champions/"

# Zeri - The Spark of Zaun
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zeri",
    "release_date": "2022-01-20",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 80,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zeri_0.jpg",
    "description": "The spark of Zaun",
    "win_rate": 48.2,
    "pick_rate": 12.1,
    "ban_rate": 8.5
  }'

# Jinx - The Loose Cannon
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jinx",
    "release_date": "2013-10-10",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 75,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Jinx_0.jpg",
    "description": "The Loose Cannon",
    "win_rate": 51.3,
    "pick_rate": 18.7,
    "ban_rate": 15.2
  }'

# Yasuo - The Unforgiven
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yasuo",
    "release_date": "2013-12-13",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 85,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yasuo_0.jpg",
    "description": "The Unforgiven",
    "win_rate": 49.8,
    "pick_rate": 25.4,
    "ban_rate": 35.7
  }'

# Thresh - The Chain Warden
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thresh",
    "release_date": "2013-01-23",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "tank",
    "difficulty": "hard",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Thresh_0.jpg",
    "description": "The Chain Warden",
    "win_rate": 50.1,
    "pick_rate": 22.3,
    "ban_rate": 12.8
  }'

# Lee Sin - The Blind Monk
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lee Sin",
    "release_date": "2011-04-01",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 82,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/LeeSin_0.jpg",
    "description": "The Blind Monk",
    "win_rate": 47.9,
    "pick_rate": 16.5,
    "ban_rate": 18.9
  }'

# Ahri - The Nine-Tailed Fox
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ahri",
    "release_date": "2011-12-14",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ahri_0.jpg",
    "description": "The Nine-Tailed Fox",
    "win_rate": 52.1,
    "pick_rate": 14.3,
    "ban_rate": 6.7
  }'

# Garen - The Might of Demacia
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Garen",
    "release_date": "2010-04-27",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 65,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Garen_0.jpg",
    "description": "The Might of Demacia",
    "win_rate": 51.8,
    "pick_rate": 8.9,
    "ban_rate": 4.2
  }'

# Vayne - The Night Hunter
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vayne",
    "release_date": "2011-05-10",
    "primary_role": "adc",
    "secondary_role": "top",
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 83,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Vayne_0.jpg",
    "description": "The Night Hunter",
    "win_rate": 50.5,
    "pick_rate": 19.2,
    "ban_rate": 22.1
  }'

# Katarina - The Sinister Blade
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Katarina",
    "release_date": "2009-09-19",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": "mage",
    "difficulty": "hard",
    "strength": 79,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Katarina_0.jpg",
    "description": "The Sinister Blade",
    "win_rate": 52.3,
    "pick_rate": 11.8,
    "ban_rate": 28.4
  }'

# Blitzcrank - The Great Steam Golem
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blitzcrank",
    "release_date": "2009-09-02",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 70,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Blitzcrank_0.jpg",
    "description": "The Great Steam Golem",
    "win_rate": 51.9,
    "pick_rate": 13.4,
    "ban_rate": 16.8
  }'

# Darius - The Hand of Noxus
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Darius",
    "release_date": "2012-05-23",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Darius_0.jpg",
    "description": "The Hand of Noxus",
    "win_rate": 50.9,
    "pick_rate": 14.2,
    "ban_rate": 19.3
  }'

# Lux - The Lady of Luminosity
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lux",
    "release_date": "2010-10-19",
    "primary_role": "mid",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "easy",
    "strength": 68,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lux_0.jpg",
    "description": "The Lady of Luminosity",
    "win_rate": 51.5,
    "pick_rate": 17.8,
    "ban_rate": 7.2
  }'

# Graves - The Outlaw
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Graves",
    "release_date": "2011-10-19",
    "primary_role": "jungle",
    "secondary_role": "adc",
    "champion_type1": "marksman",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 76,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Graves_0.jpg",
    "description": "The Outlaw",
    "win_rate": 50.7,
    "pick_rate": 13.9,
    "ban_rate": 11.4
  }'

# Leona - The Radiant Dawn
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Leona",
    "release_date": "2011-07-13",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "support",
    "difficulty": "easy",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Leona_0.jpg",
    "description": "The Radiant Dawn",
    "win_rate": 52.8,
    "pick_rate": 15.6,
    "ban_rate": 8.9
  }'

# Azir - The Emperor of the Sands
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Azir",
    "release_date": "2014-09-16",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": "marksman",
    "difficulty": "hard",
    "strength": 87,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Azir_0.jpg",
    "description": "The Emperor of the Sands",
    "win_rate": 46.3,
    "pick_rate": 4.2,
    "ban_rate": 2.1
  }'

# Fiora - The Grand Duelist
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fiora",
    "release_date": "2012-02-29",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 81,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Fiora_0.jpg",
    "description": "The Grand Duelist",
    "win_rate": 50.2,
    "pick_rate": 9.7,
    "ban_rate": 14.8
  }'

# Jhin - The Virtuoso
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jhin",
    "release_date": "2016-02-01",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 77,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Jhin_0.jpg",
    "description": "The Virtuoso",
    "win_rate": 51.8,
    "pick_rate": 20.4,
    "ban_rate": 13.7
  }'

# Zed - The Master of Shadows
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zed",
    "release_date": "2012-11-13",
    "primary_role": "mid",
    "secondary_role": "jungle",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 84,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zed_0.jpg",
    "description": "The Master of Shadows",
    "win_rate": 49.1,
    "pick_rate": 13.2,
    "ban_rate": 31.5
  }'

# Braum - The Heart of the Freljord
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Braum",
    "release_date": "2014-05-12",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 69,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Braum_0.jpg",
    "description": "The Heart of the Freljord",
    "win_rate": 51.2,
    "pick_rate": 11.8,
    "ban_rate": 5.3
  }'

# Ekko - The Boy Who Shattered Time
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ekko",
    "release_date": "2015-05-28",
    "primary_role": "jungle",
    "secondary_role": "mid",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ekko_0.jpg",
    "description": "The Boy Who Shattered Time",
    "win_rate": 50.6,
    "pick_rate": 12.4,
    "ban_rate": 9.8
  }'

# Riven - The Exile
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Riven",
    "release_date": "2011-09-14",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 86,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Riven_0.jpg",
    "description": "The Exile",
    "win_rate": 50.8,
    "pick_rate": 11.3,
    "ban_rate": 17.2
  }'

# Caitlyn - The Sheriff of Piltover
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Caitlyn",
    "release_date": "2011-01-04",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Caitlyn_0.jpg",
    "description": "The Sheriff of Piltover",
    "win_rate": 50.3,
    "pick_rate": 16.8,
    "ban_rate": 9.1
  }'

# Twisted Fate - The Card Master
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Twisted Fate",
    "release_date": "2009-02-21",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/TwistedFate_0.jpg",
    "description": "The Card Master",
    "win_rate": 51.7,
    "pick_rate": 7.6,
    "ban_rate": 3.4
  }'

# Kassadin - The Void Walker
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kassadin",
    "release_date": "2009-08-07",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kassadin_0.jpg",
    "description": "The Void Walker",
    "win_rate": 51.9,
    "pick_rate": 6.8,
    "ban_rate": 12.3
  }'

# Morgana - The Fallen
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morgana",
    "release_date": "2009-02-21",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "easy",
    "strength": 67,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Morgana_0.jpg",
    "description": "The Fallen",
    "win_rate": 51.4,
    "pick_rate": 14.7,
    "ban_rate": 21.6
  }'

# Viktor - The Machine Herald
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viktor",
    "release_date": "2011-12-29",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 82,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Viktor_0.jpg",
    "description": "The Machine Herald",
    "win_rate": 52.1,
    "pick_rate": 8.3,
    "ban_rate": 6.7
  }'

# Draven - The Glorious Executioner
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Draven",
    "release_date": "2012-06-06",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 85,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Draven_0.jpg",
    "description": "The Glorious Executioner",
    "win_rate": 49.8,
    "pick_rate": 7.2,
    "ban_rate": 11.4
  }'

# Irelia - The Blade Dancer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Irelia",
    "release_date": "2010-11-16",
    "primary_role": "top",
    "secondary_role": "mid",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 79,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Irelia_0.jpg",
    "description": "The Blade Dancer",
    "win_rate": 48.9,
    "pick_rate": 10.7,
    "ban_rate": 18.3
  }'

# Sejuani - Fury of the North
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sejuani",
    "release_date": "2012-01-17",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "easy",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sejuani_0.jpg",
    "description": "Fury of the North",
    "win_rate": 51.6,
    "pick_rate": 9.4,
    "ban_rate": 7.8
  }'

# Syndra - The Dark Sovereign
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Syndra",
    "release_date": "2012-09-13",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 83,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Syndra_0.jpg",
    "description": "The Dark Sovereign",
    "win_rate": 49.2,
    "pick_rate": 6.9,
    "ban_rate": 14.1
  }'

# Rengar - The Pridestalker
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rengar",
    "release_date": "2012-08-21",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 81,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Rengar_0.jpg",
    "description": "The Pridestalker",
    "win_rate": 48.7,
    "pick_rate": 8.1,
    "ban_rate": 22.9
  }'

# Nami - The Tidecaller
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nami",
    "release_date": "2012-12-07",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 68,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nami_0.jpg",
    "description": "The Tidecaller",
    "win_rate": 52.3,
    "pick_rate": 16.7,
    "ban_rate": 4.2
  }'

# Camille - The Steel Shadow
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Camille",
    "release_date": "2016-12-07",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 84,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Camille_0.jpg",
    "description": "The Steel Shadow",
    "win_rate": 50.1,
    "pick_rate": 7.8,
    "ban_rate": 16.5
  }'

# Kha'Zix - The Voidreaver
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kha Zix",
    "release_date": "2012-09-27",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 76,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Khazix_0.jpg",
    "description": "The Voidreaver",
    "win_rate": 50.8,
    "pick_rate": 12.3,
    "ban_rate": 13.7
  }'

# Orianna - The Lady of Clockwork
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Orianna",
    "release_date": "2011-06-01",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "hard",
    "strength": 80,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Orianna_0.jpg",
    "description": "The Lady of Clockwork",
    "win_rate": 49.7,
    "pick_rate": 5.4,
    "ban_rate": 3.8
  }'

# Malphite - Shard of the Monolith
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Malphite",
    "release_date": "2009-09-02",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "tank",
    "champion_type2": "mage",
    "difficulty": "easy",
    "strength": 66,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Malphite_0.jpg",
    "description": "Shard of the Monolith",
    "win_rate": 52.4,
    "pick_rate": 11.2,
    "ban_rate": 8.6
  }'

# Ezreal - The Prodigal Explorer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ezreal",
    "release_date": "2010-03-16",
    "primary_role": "adc",
    "secondary_role": "mid",
    "champion_type1": "marksman",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ezreal_0.jpg",
    "description": "The Prodigal Explorer",
    "win_rate": 48.6,
    "pick_rate": 22.1,
    "ban_rate": 5.9
  }'

# Diana - Scorn of the Moon
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Diana",
    "release_date": "2012-08-07",
    "primary_role": "jungle",
    "secondary_role": "mid",
    "champion_type1": "fighter",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 75,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Diana_0.jpg",
    "description": "Scorn of the Moon",
    "win_rate": 51.2,
    "pick_rate": 9.8,
    "ban_rate": 7.3
  }'

# Shen - The Eye of Twilight
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Shen",
    "release_date": "2010-03-24",
    "primary_role": "top",
    "secondary_role": "support",
    "champion_type1": "tank",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 69,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Shen_0.jpg",
    "description": "The Eye of Twilight",
    "win_rate": 51.8,
    "pick_rate": 6.7,
    "ban_rate": 4.1
  }'

# Jax - Grandmaster at Arms
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jax",
    "release_date": "2009-02-21",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": null,
    "difficulty": "easy",
    "strength": 77,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Jax_0.jpg",
    "description": "Grandmaster at Arms",
    "win_rate": 50.9,
    "pick_rate": 13.4,
    "ban_rate": 12.8
  }'

# Annie - The Dark Child
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Annie",
    "release_date": "2009-02-21",
    "primary_role": "mid",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "easy",
    "strength": 63,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Annie_0.jpg",
    "description": "The Dark Child",
    "win_rate": 51.7,
    "pick_rate": 4.8,
    "ban_rate": 2.3
  }'

# Lucian - The Purifier
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lucian",
    "release_date": "2013-08-22",
    "primary_role": "adc",
    "secondary_role": "mid",
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lucian_0.jpg",
    "description": "The Purifier",
    "win_rate": 49.3,
    "pick_rate": 19.7,
    "ban_rate": 7.4
  }'

# Zyra - Rise of the Thorns
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zyra",
    "release_date": "2012-07-24",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zyra_0.jpg",
    "description": "Rise of the Thorns",
    "win_rate": 52.1,
    "pick_rate": 8.9,
    "ban_rate": 6.2
  }'

# Akali - The Rogue Assassin
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Akali",
    "release_date": "2010-05-11",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "assassin",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 86,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Akali_0.jpg",
    "description": "The Rogue Assassin",
    "win_rate": 47.8,
    "pick_rate": 9.4,
    "ban_rate": 26.3
  }'

# Veigar - The Tiny Master of Evil
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Veigar",
    "release_date": "2009-07-24",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Veigar_0.jpg",
    "description": "The Tiny Master of Evil",
    "win_rate": 52.6,
    "pick_rate": 7.1,
    "ban_rate": 5.8
  }'

# Hecarim - The Shadow of War
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hecarim",
    "release_date": "2012-04-18",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Hecarim_0.jpg",
    "description": "The Shadow of War",
    "win_rate": 51.3,
    "pick_rate": 10.2,
    "ban_rate": 8.7
  }'

# Brand - The Burning Vengeance
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brand",
    "release_date": "2011-04-12",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 70,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Brand_0.jpg",
    "description": "The Burning Vengeance",
    "win_rate": 51.9,
    "pick_rate": 12.6,
    "ban_rate": 9.4
  }'

# Teemo - The Swift Scout
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teemo",
    "release_date": "2009-02-21",
    "primary_role": "top",
    "secondary_role": "adc",
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "easy",
    "strength": 61,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Teemo_0.jpg",
    "description": "The Swift Scout",
    "win_rate": 50.4,
    "pick_rate": 6.8,
    "ban_rate": 11.7
  }'

# Kayn - The Shadow Reaper
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kayn",
    "release_date": "2017-07-12",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 79,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kayn_0.jpg",
    "description": "The Shadow Reaper",
    "win_rate": 50.7,
    "pick_rate": 14.1,
    "ban_rate": 10.3
  }'

# Soraka - The Starchild
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Soraka",
    "release_date": "2009-02-21",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "easy",
    "strength": 64,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Soraka_0.jpg",
    "description": "The Starchild",
    "win_rate": 52.8,
    "pick_rate": 13.9,
    "ban_rate": 7.1
  }'

# Yone - The Unforgotten
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yone",
    "release_date": "2020-08-06",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 83,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yone_0.jpg",
    "description": "The Unforgotten",
    "win_rate": 49.6,
    "pick_rate": 15.2,
    "ban_rate": 21.8
  }'

# Samira - The Desert Rose
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Samira",
    "release_date": "2020-09-21",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 84,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Samira_0.jpg",
    "description": "The Desert Rose",
    "win_rate": 48.7,
    "pick_rate": 9.4,
    "ban_rate": 18.6
  }'

# Aphelios - The Weapon of the Faithful
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aphelios",
    "release_date": "2019-12-11",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 87,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aphelios_0.jpg",
    "description": "The Weapon of the Faithful",
    "win_rate": 47.3,
    "pick_rate": 6.1,
    "ban_rate": 12.4
  }'

# Pyke - The Bloodharbor Ripper
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pyke",
    "release_date": "2018-05-31",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "assassin",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 76,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Pyke_0.jpg",
    "description": "The Bloodharbor Ripper",
    "win_rate": 50.9,
    "pick_rate": 11.7,
    "ban_rate": 15.3
  }'

# Kai Sa - Daughter of the Void
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kai Sa",
    "release_date": "2018-03-07",
    "primary_role": "adc",
    "secondary_role": "jungle",
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kaisa_0.jpg",
    "description": "Daughter of the Void",
    "win_rate": 50.2,
    "pick_rate": 17.8,
    "ban_rate": 11.9
  }'

# Xayah - The Rebel
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Xayah",
    "release_date": "2017-04-19",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 75,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Xayah_0.jpg",
    "description": "The Rebel",
    "win_rate": 50.8,
    "pick_rate": 13.2,
    "ban_rate": 7.4
  }'

# Rakan - The Charmer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rakan",
    "release_date": "2017-04-19",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "hard",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Rakan_0.jpg",
    "description": "The Charmer",
    "win_rate": 51.4,
    "pick_rate": 8.9,
    "ban_rate": 5.6
  }'

# Ornn - The Fire Beneath the Mountain
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ornn",
    "release_date": "2017-08-23",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ornn_0.jpg",
    "description": "The Fire Beneath the Mountain",
    "win_rate": 51.7,
    "pick_rate": 7.3,
    "ban_rate": 4.8
  }'

# Sylas - The Unshackled
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sylas",
    "release_date": "2019-01-25",
    "primary_role": "mid",
    "secondary_role": "jungle",
    "champion_type1": "assassin",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 77,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sylas_0.jpg",
    "description": "The Unshackled",
    "win_rate": 48.9,
    "pick_rate": 8.7,
    "ban_rate": 13.2
  }'

# Neeko - The Curious Chameleon
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Neeko",
    "release_date": "2018-12-05",
    "primary_role": "mid",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Neeko_0.jpg",
    "description": "The Curious Chameleon",
    "win_rate": 51.3,
    "pick_rate": 5.9,
    "ban_rate": 3.7
  }'

# Yuumi - The Magical Cat
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yuumi",
    "release_date": "2019-05-14",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "easy",
    "strength": 62,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yuumi_0.jpg",
    "description": "The Magical Cat",
    "win_rate": 48.4,
    "pick_rate": 7.2,
    "ban_rate": 24.8
  }'

# Senna - The Redeemer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senna",
    "release_date": "2019-11-10",
    "primary_role": "support",
    "secondary_role": "adc",
    "champion_type1": "support",
    "champion_type2": "marksman",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Senna_0.jpg",
    "description": "The Redeemer",
    "win_rate": 50.6,
    "pick_rate": 14.3,
    "ban_rate": 8.1
  }'

# Viego - The Ruined King
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viego",
    "release_date": "2021-01-22",
    "primary_role": "jungle",
    "secondary_role": "mid",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 80,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Viego_0.jpg",
    "description": "The Ruined King",
    "win_rate": 49.8,
    "pick_rate": 10.4,
    "ban_rate": 16.7
  }'

# Rell - The Iron Maiden
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rell",
    "release_date": "2020-12-10",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Rell_0.jpg",
    "description": "The Iron Maiden",
    "win_rate": 51.0,
    "pick_rate": 8.2,
    "ban_rate": 6.9
  }'

# Akshan - The Rogue Sentinel
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Akshan",
    "release_date": "2021-07-22",
    "primary_role": "mid",
    "secondary_role": "adc",
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "hard",
    "strength": 79,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Akshan_0.jpg",
    "description": "The Rogue Sentinel",
    "win_rate": 49.2,
    "pick_rate": 7.4,
    "ban_rate": 9.6
  }'

# Vex - The Gloomist
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vex",
    "release_date": "2021-09-23",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Vex_0.jpg",
    "description": "The Gloomist",
    "win_rate": 50.8,
    "pick_rate": 6.3,
    "ban_rate": 4.7
  }'

# Renata Glasc - The Chem-Baroness
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Renata Glasc",
    "release_date": "2022-02-17",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 75,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Renata_0.jpg",
    "description": "The Chem-Baroness",
    "win_rate": 50.9,
    "pick_rate": 9.1,
    "ban_rate": 6.4
  }'

# Bel'Veth - Empress of the Void
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Bel'Veth","release_date": "2022-06-09","primary_role": "jungle","secondary_role": null,"champion_type1": "fighter","champion_type2": "assassin","difficulty": "hard","strength": 82,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Belveth_0.jpg","description": "Empress of the Void","win_rate": 49.4,"pick_rate": 8.5,"ban_rate": 12.7}
JSON

# Nilah - The Joy Unbound
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nilah",
    "release_date": "2022-07-13",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nilah_0.jpg",
    "description": "The Joy Unbound",
    "win_rate": 50.1,
    "pick_rate": 5.6,
    "ban_rate": 7.8
  }'

# K'Sante - The Pride of Nazumah
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "K'Sante","release_date": "2022-11-03","primary_role": "top","secondary_role": null,"champion_type1": "tank","champion_type2": "fighter","difficulty": "hard","strength": 81,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/KSante_0.jpg","description": "The Pride of Nazumah","win_rate": 49.1,"pick_rate": 7.9,"ban_rate": 10.5}
JSON

# Milio - The Gentle Flame
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Milio",
    "release_date": "2023-03-23",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "easy",
    "strength": 66,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Milio_0.jpg",
    "description": "The Gentle Flame",
    "win_rate": 51.5,
    "pick_rate": 6.8,
    "ban_rate": 5.1
  }'

# Naafiri - The Hound of a Hundred Bites
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Naafiri",
    "release_date": "2023-07-20",
    "primary_role": "mid",
    "secondary_role": "jungle",
    "champion_type1": "assassin",
    "champion_type2": null,
    "difficulty": "easy",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Naafiri_0.jpg",
    "description": "The Hound of a Hundred Bites",
    "win_rate": 50.0,
    "pick_rate": 5.3,
    "ban_rate": 6.6
  }'

# Briar - The Restrained Hunger
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Briar",
    "release_date": "2023-09-14",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 77,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Briar_0.jpg",
    "description": "The Restrained Hunger",
    "win_rate": 49.6,
    "pick_rate": 6.9,
    "ban_rate": 8.2
  }'

# Hwei - The Visionary
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hwei",
    "release_date": "2023-12-13",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 80,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Hwei_0.jpg",
    "description": "The Visionary",
    "win_rate": 49.0,
    "pick_rate": 5.7,
    "ban_rate": 7.5
  }'

# Smolder - The Fiery Fledgling
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smolder",
    "release_date": "2024-01-31",
    "primary_role": "adc",
    "secondary_role": null,
    "champion_type1": "marksman",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Smolder_0.jpg",
    "description": "The Fiery Fledgling",
    "win_rate": 50.4,
    "pick_rate": 12.7,
    "ban_rate": 9.9
  }'

# Aurora - The Witch Between Worlds
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aurora",
    "release_date": "2024-07-17",
    "primary_role": "mid",
    "secondary_role": "jungle",
    "champion_type1": "mage",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 78,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aurora_0.jpg",
    "description": "The Witch Between Worlds",
    "win_rate": 50.2,
    "pick_rate": 8.1,
    "ban_rate": 7.3
  }'

# Gwen - The Hallowed Seamstress
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gwen",
    "release_date": "2021-04-15",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 76,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gwen_0.jpg",
    "description": "The Hallowed Seamstress",
    "win_rate": 48.1,
    "pick_rate": 6.8,
    "ban_rate": 9.5
  }'

 

# Warwick - The Uncaged Wrath of Zaun
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Warwick",
    "release_date": "2009-02-21",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 70,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Warwick_0.jpg",
    "description": "The Uncaged Wrath of Zaun",
    "win_rate": 52.3,
    "pick_rate": 12.7,
    "ban_rate": 6.9
  }'

# Master Yi - The Wuju Bladesman
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Master Yi",
    "release_date": "2009-02-21",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "easy",
    "strength": 68,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/MasterYi_0.jpg",
    "description": "The Wuju Bladesman",
    "win_rate": 51.8,
    "pick_rate": 11.4,
    "ban_rate": 19.7
  }'

# Tryndamere - The Barbarian King
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tryndamere",
    "release_date": "2009-05-01",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "easy",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Tryndamere_0.jpg",
    "description": "The Barbarian King",
    "win_rate": 50.1,
    "pick_rate": 8.3,
    "ban_rate": 12.6
  }'

# Nasus - The Curator of the Sands
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nasus",
    "release_date": "2009-10-01",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 69,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nasus_0.jpg",
    "description": "The Curator of the Sands",
    "win_rate": 52.4,
    "pick_rate": 9.6,
    "ban_rate": 7.8
  }'

# Vladimir - The Crimson Reaper
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vladimir",
    "release_date": "2010-07-27",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "mage",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 75,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Vladimir_0.jpg",
    "description": "The Crimson Reaper",
    "win_rate": 51.2,
    "pick_rate": 6.9,
    "ban_rate": 8.4
  }'

# Swain - The Noxian Grand General
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Swain",
    "release_date": "2010-10-05",
    "primary_role": "mid",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Swain_0.jpg",
    "description": "The Noxian Grand General",
    "win_rate": 51.7,
    "pick_rate": 5.8,
    "ban_rate": 4.2
  }'

# Zilean - The Chronokeeper
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zilean",
    "release_date": "2009-04-18",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 67,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zilean_0.jpg",
    "description": "The Chronokeeper",
    "win_rate": 52.9,
    "pick_rate": 3.4,
    "ban_rate": 2.1
  }'

# Qiyana - Empress of the Elements
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Qiyana",
    "release_date": "2019-06-28",
    "primary_role": "mid",
    "secondary_role": "jungle",
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 82,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Qiyana_0.jpg",
    "description": "Empress of the Elements",
    "win_rate": 48.3,
    "pick_rate": 5.7,
    "ban_rate": 14.9
  }'

 

# Lillia - The Bashful Bloom
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lillia",
    "release_date": "2020-07-22",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lillia_0.jpg",
    "description": "The Bashful Bloom",
    "win_rate": 49.4,
    "pick_rate": 4.9,
    "ban_rate": 5.8
  }'

# Aatrox - The Darkin Blade
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aatrox",
    "release_date": "2013-06-13",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "medium",
    "strength": 77,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aatrox_0.jpg",
    "description": "The Darkin Blade",
    "win_rate": 49.7,
    "pick_rate": 8.9,
    "ban_rate": 13.2
  }'

# Bard - The Wandering Caretaker
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bard",
    "release_date": "2015-03-12",
    "primary_role": "support",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "hard",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Bard_0.jpg",
    "description": "The Wandering Caretaker",
    "win_rate": 51.8,
    "pick_rate": 6.4,
    "ban_rate": 3.7
  }'

# Cassiopeia - The Serpent's Embrace
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cassiopeia",
    "release_date": "2010-12-14",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 81,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Cassiopeia_0.jpg",
    "description": "The Serpent Embrace",
    "win_rate": 52.3,
    "pick_rate": 4.1,
    "ban_rate": 7.8
  }'

# Dr. Mundo - The Madman of Zaun
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Mundo",
    "release_date": "2009-09-02",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 68,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/DrMundo_0.jpg",
    "description": "The Madman of Zaun",
    "win_rate": 51.9,
    "pick_rate": 7.2,
    "ban_rate": 5.3
  }'

# Elise - The Spider Queen
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Elise",
    "release_date": "2012-10-26",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "mage",
    "champion_type2": "fighter",
    "difficulty": "hard",
    "strength": 79,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Elise_0.jpg",
    "description": "The Spider Queen",
    "win_rate": 49.4,
    "pick_rate": 5.8,
    "ban_rate": 9.1
  }'

# Fiddlesticks - The Ancient Fear
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fiddlesticks",
    "release_date": "2009-02-21",
    "primary_role": "jungle",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Fiddlesticks_0.jpg",
    "description": "The Ancient Fear",
    "win_rate": 50.6,
    "pick_rate": 4.7,
    "ban_rate": 8.4
  }'

# Gangplank - The Saltwater Scourge
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gangplank",
    "release_date": "2009-08-19",
    "primary_role": "top",
    "secondary_role": "mid",
    "champion_type1": "fighter",
    "champion_type2": "marksman",
    "difficulty": "hard",
    "strength": 83,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gangplank_0.jpg",
    "description": "The Saltwater Scourge",
    "win_rate": 48.1,
    "pick_rate": 6.3,
    "ban_rate": 11.7
  }'

# Heimerdinger - The Revered Inventor
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Heimerdinger",
    "release_date": "2009-10-10",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "medium",
    "strength": 70,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Heimerdinger_0.jpg",
    "description": "The Revered Inventor",
    "win_rate": 52.7,
    "pick_rate": 3.9,
    "ban_rate": 4.2
  }'

# Ivern - The Green Father
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ivern",
    "release_date": "2016-10-05",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "support",
    "champion_type2": "mage",
    "difficulty": "medium",
    "strength": 69,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ivern_0.jpg",
    "description": "The Green Father",
    "win_rate": 51.4,
    "pick_rate": 2.8,
    "ban_rate": 1.9
  }'

# Jarvan IV - The Exemplar of Demacia
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jarvan IV",
    "release_date": "2011-03-01",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "easy",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/JarvanIV_0.jpg",
    "description": "The Exemplar of Demacia",
    "win_rate": 50.9,
    "pick_rate": 8.7,
    "ban_rate": 6.4
  }'

# Karma - The Enlightened One
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Karma",
    "release_date": "2011-02-01",
    "primary_role": "support",
    "secondary_role": "mid",
    "champion_type1": "mage",
    "champion_type2": "support",
    "difficulty": "easy",
    "strength": 66,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Karma_0.jpg",
    "description": "The Enlightened One",
    "win_rate": 50.8,
    "pick_rate": 9.3,
    "ban_rate": 4.7
  }'

# LeBlanc - The Deceiver
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LeBlanc",
    "release_date": "2010-11-02",
    "primary_role": "mid",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": "mage",
    "difficulty": "hard",
    "strength": 85,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Leblanc_0.jpg",
    "description": "The Deceiver",
    "win_rate": 48.9,
    "pick_rate": 7.1,
    "ban_rate": 17.3
  }'

# Maokai - The Twisted Treant
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maokai",
    "release_date": "2011-02-16",
    "primary_role": "top",
    "secondary_role": "support",
    "champion_type1": "tank",
    "champion_type2": "mage",
    "difficulty": "easy",
    "strength": 67,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Maokai_0.jpg",
    "description": "The Twisted Treant",
    "win_rate": 52.1,
    "pick_rate": 5.9,
    "ban_rate": 3.8
  }'

# Nocturne - The Eternal Nightmare
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nocturne",
    "release_date": "2011-03-15",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "assassin",
    "champion_type2": "fighter",
    "difficulty": "easy",
    "strength": 73,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nocturne_0.jpg",
    "description": "The Eternal Nightmare",
    "win_rate": 51.7,
    "pick_rate": 9.2,
    "ban_rate": 10.6
  }'

# Olaf - The Berserker
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Olaf",
    "release_date": "2010-06-09",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "easy",
    "strength": 70,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Olaf_0.jpg",
    "description": "The Berserker",
    "win_rate": 50.3,
    "pick_rate": 6.8,
    "ban_rate": 5.1
  }'

# Pantheon - The Unbreakable Spear
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pantheon",
    "release_date": "2010-02-02",
    "primary_role": "mid",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "easy",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Pantheon_0.jpg",
    "description": "The Unbreakable Spear",
    "win_rate": 49.8,
    "pick_rate": 7.4,
    "ban_rate": 8.9
  }'

# Quinn - Demacia's Wings
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quinn",
    "release_date": "2013-10-03",
    "primary_role": "top",
    "secondary_role": "adc",
    "champion_type1": "marksman",
    "champion_type2": "assassin",
    "difficulty": "medium",
    "strength": 72,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Quinn_0.jpg",
    "description": "Demacia Wings",
    "win_rate": 51.6,
    "pick_rate": 3.7,
    "ban_rate": 4.8
  }'

# Rammus - The Armordillo
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rammus",
    "release_date": "2009-07-10",
    "primary_role": "jungle",
    "secondary_role": null,
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "easy",
    "strength": 65,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Rammus_0.jpg",
    "description": "The Armordillo",
    "win_rate": 52.8,
    "pick_rate": 4.9,
    "ban_rate": 3.2
  }'

# Sion - The Undead Juggernaut
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sion",
    "release_date": "2009-02-21",
    "primary_role": "top",
    "secondary_role": "support",
    "champion_type1": "tank",
    "champion_type2": "fighter",
    "difficulty": "medium",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sion_0.jpg",
    "description": "The Undead Juggernaut",
    "win_rate": 51.4,
    "pick_rate": 6.1,
    "ban_rate": 4.6
  }'

# Taliyah - The Stoneweaver
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Taliyah",
    "release_date": "2016-05-18",
    "primary_role": "jungle",
    "secondary_role": "mid",
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "hard",
    "strength": 76,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Taliyah_0.jpg",
    "description": "The Stoneweaver",
    "win_rate": 50.9,
    "pick_rate": 3.4,
    "ban_rate": 2.7
  }'

# Udyr - The Spirit Walker
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Udyr",
    "release_date": "2009-12-02",
    "primary_role": "jungle",
    "secondary_role": "top",
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "medium",
    "strength": 68,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Udyr_0.jpg",
    "description": "The Spirit Walker",
    "win_rate": 49.7,
    "pick_rate": 4.2,
    "ban_rate": 6.3
  }'

# Vel'Koz - The Eye of the Void
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Vel'Koz","release_date": "2014-02-27","primary_role": "mid","secondary_role": "support","champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 75,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Velkoz_0.jpg","description": "The Eye of the Void","win_rate": 52.4,"pick_rate": 4.6,"ban_rate": 3.1}
JSON

# Wukong - The Monkey King
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wukong",
    "release_date": "2011-07-26",
    "primary_role": "top",
    "secondary_role": "jungle",
    "champion_type1": "fighter",
    "champion_type2": "assassin",
    "difficulty": "easy",
    "strength": 71,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/MonkeyKing_0.jpg",
    "description": "The Monkey King",
    "win_rate": 51.2,
    "pick_rate": 7.8,
    "ban_rate": 9.4
  }'

# Xerath - The Magus Ascendant
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Xerath",
    "release_date": "2011-10-05",
    "primary_role": "mid",
    "secondary_role": "support",
    "champion_type1": "mage",
    "champion_type2": null,
    "difficulty": "medium",
    "strength": 74,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Xerath_0.jpg",
    "description": "The Magus Ascendant",
    "win_rate": 50.7,
    "pick_rate": 6.9,
    "ban_rate": 5.8
  }'

# Yorick - The Shepherd of Souls
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yorick",
    "release_date": "2011-06-22",
    "primary_role": "top",
    "secondary_role": null,
    "champion_type1": "fighter",
    "champion_type2": "tank",
    "difficulty": "medium",
    "strength": 69,
    "image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yorick_0.jpg",
    "description": "The Shepherd of Souls",
    "win_rate": 52.6,
    "pick_rate": 3.8,
    "ban_rate": 4.1
  }'

# Alistar - the Minotaur
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Alistar","release_date": "2009-02-21","primary_role": "support","secondary_role": null,"champion_type1": "tank","champion_type2": "support","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Alistar_0.jpg","description": "the Minotaur","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Ambessa - Matriarch of War
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Ambessa","release_date": "2024-11-06","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "assassin","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ambessa_0.jpg","description": "Matriarch of War","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Amumu - the Sad Mummy
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Amumu","release_date": "2009-06-26","primary_role": "jungle","secondary_role": "support","champion_type1": "tank","champion_type2": "support","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Amumu_0.jpg","description": "the Sad Mummy","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Anivia - the Cryophoenix
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Anivia","release_date": "2009-07-10","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Anivia_0.jpg","description": "the Cryophoenix","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Ashe - the Frost Archer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Ashe","release_date": "2009-02-21","primary_role": "adc","secondary_role": "support","champion_type1": "marksman","champion_type2": "support","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ashe_0.jpg","description": "the Frost Archer","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Aurelion Sol - The Star Forger
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Aurelion Sol","release_date": "2016-03-24","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/AurelionSol_0.jpg","description": "The Star Forger","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Cho'Gath - the Terror of the Void
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Cho'Gath","release_date": "2009-06-26","primary_role": "top","secondary_role": null,"champion_type1": "tank","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Chogath_0.jpg","description": "the Terror of the Void","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Corki - the Daring Bombardier
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Corki","release_date": "2009-09-19","primary_role": "mid","secondary_role": null,"champion_type1": "marksman","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Corki_0.jpg","description": "the Daring Bombardier","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Evelynn - Agony's Embrace
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Evelynn","release_date": "2009-05-01","primary_role": "jungle","secondary_role": null,"champion_type1": "assassin","champion_type2": "mage","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Evelynn_0.jpg","description": "Agony's Embrace","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Fizz - the Tidal Trickster
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Fizz","release_date": "2011-11-15","primary_role": "mid","secondary_role": null,"champion_type1": "assassin","champion_type2": "fighter","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Fizz_0.jpg","description": "the Tidal Trickster","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Galio - the Colossus
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Galio","release_date": "2010-08-10","primary_role": "mid","secondary_role": "support","champion_type1": "tank","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Galio_0.jpg","description": "the Colossus","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Gnar - the Missing Link
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Gnar","release_date": "2014-08-14","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gnar_0.jpg","description": "the Missing Link","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Gragas - the Rabble Rouser
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Gragas","release_date": "2010-02-02","primary_role": "jungle","secondary_role": "mid","champion_type1": "fighter","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gragas_0.jpg","description": "the Rabble Rouser","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Illaoi - the Kraken Priestess
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Illaoi","release_date": "2015-11-24","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Illaoi_0.jpg","description": "the Kraken Priestess","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Janna - the Storm's Fury
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Janna","release_date": "2009-09-02","primary_role": "support","secondary_role": null,"champion_type1": "support","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Janna_0.jpg","description": "the Storm's Fury","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Jayce - the Defender of Tomorrow
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Jayce","release_date": "2012-07-07","primary_role": "mid","secondary_role": "top","champion_type1": "fighter","champion_type2": "marksman","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Jayce_0.jpg","description": "the Defender of Tomorrow","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kalista - the Spear of Vengeance
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kalista","release_date": "2014-11-20","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kalista_0.jpg","description": "the Spear of Vengeance","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Karthus - the Deathsinger
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Karthus","release_date": "2009-06-12","primary_role": "jungle","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Karthus_0.jpg","description": "the Deathsinger","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kayle - the Righteous
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kayle","release_date": "2009-02-21","primary_role": "top","secondary_role": null,"champion_type1": "mage","champion_type2": "marksman","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kayle_0.jpg","description": "the Righteous","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kennen - the Heart of the Tempest
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kennen","release_date": "2010-04-08","primary_role": "top","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kennen_0.jpg","description": "the Heart of the Tempest","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kindred - The Eternal Hunters
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kindred","release_date": "2015-10-14","primary_role": "jungle","secondary_role": null,"champion_type1": "marksman","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kindred_0.jpg","description": "The Eternal Hunters","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kled - the Cantankerous Cavalier
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kled","release_date": "2016-08-10","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kled_0.jpg","description": "the Cantankerous Cavalier","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Kog'Maw - the Mouth of the Abyss
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Kog'Maw","release_date": "2010-06-24","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/KogMaw_0.jpg","description": "the Mouth of the Abyss","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Lissandra - the Ice Witch
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Lissandra","release_date": "2013-04-30","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lissandra_0.jpg","description": "the Ice Witch","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Lulu - the Fae Sorceress
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Lulu","release_date": "2012-03-20","primary_role": "support","secondary_role": null,"champion_type1": "support","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lulu_0.jpg","description": "the Fae Sorceress","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Malzahar - the Prophet of the Void
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Malzahar","release_date": "2010-06-01","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Malzahar_0.jpg","description": "the Prophet of the Void","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Mel - the Soul's Reflection
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Mel","release_date": "2025-01-23","primary_role": "mid","secondary_role": "support","champion_type1": "mage","champion_type2": "support","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Mel_0.jpg","description": "the Soul's Reflection","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Miss Fortune - the Bounty Hunter
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Miss Fortune","release_date": "2010-09-08","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": "mage","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/MissFortune_0.jpg","description": "the Bounty Hunter","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Mordekaiser - the Iron Revenant
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Mordekaiser","release_date": "2010-02-24","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Mordekaiser_0.jpg","description": "the Iron Revenant","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Nautilus - the Titan of the Depths
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Nautilus","release_date": "2012-02-14","primary_role": "support","secondary_role": null,"champion_type1": "tank","champion_type2": "support","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nautilus_0.jpg","description": "the Titan of the Depths","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Nidalee - the Bestial Huntress
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Nidalee","release_date": "2009-12-17","primary_role": "jungle","secondary_role": null,"champion_type1": "assassin","champion_type2": "mage","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nidalee_0.jpg","description": "the Bestial Huntress","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Nunu & Willump - the Boy and His Yeti
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Nunu & Willump","release_date": "2009-02-21","primary_role": "jungle","secondary_role": null,"champion_type1": "tank","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nunu_0.jpg","description": "the Boy and His Yeti","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Poppy - Keeper of the Hammer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Poppy","release_date": "2010-01-13","primary_role": "jungle","secondary_role": "top","champion_type1": "tank","champion_type2": "fighter","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Poppy_0.jpg","description": "Keeper of the Hammer","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Rek'Sai - the Void Burrower
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Rek'Sai","release_date": "2014-12-11","primary_role": "jungle","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/RekSai_0.jpg","description": "the Void Burrower","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Renekton - the Butcher of the Sands
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Renekton","release_date": "2011-01-18","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Renekton_0.jpg","description": "the Butcher of the Sands","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Rumble - the Mechanized Menace
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Rumble","release_date": "2011-04-26","primary_role": "mid","secondary_role": "top","champion_type1": "fighter","champion_type2": "mage","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Rumble_0.jpg","description": "the Mechanized Menace","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Ryze - the Rune Mage
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Ryze","release_date": "2009-02-21","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ryze_0.jpg","description": "the Rune Mage","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Skarner - the Primordial Sovereign
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Skarner","release_date": "2011-08-09","primary_role": "jungle","secondary_role": "top","champion_type1": "tank","champion_type2": "fighter","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Skarner_0.jpg","description": "the Primordial Sovereign","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Sona - Maven of the Strings
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Sona","release_date": "2010-09-21","primary_role": "support","secondary_role": null,"champion_type1": "support","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sona_0.jpg","description": "Maven of the Strings","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Tahm Kench - The River King
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Tahm Kench","release_date": "2015-07-09","primary_role": "support","secondary_role": "top","champion_type1": "tank","champion_type2": "support","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/TahmKench_0.jpg","description": "The River King","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Talon - the Blade's Shadow
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Talon","release_date": "2011-08-24","primary_role": "jungle","secondary_role": null,"champion_type1": "assassin","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Talon_0.jpg","description": "the Blade's Shadow","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Taric - the Shield of Valoran
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Taric","release_date": "2009-08-19","primary_role": "mid","secondary_role": "support","champion_type1": "support","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Taric_0.jpg","description": "the Shield of Valoran","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Tristana - the Yordle Gunner
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Tristana","release_date": "2009-02-21","primary_role": "adc","secondary_role": "mid","champion_type1": "marksman","champion_type2": "assassin","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Tristana_0.jpg","description": "the Yordle Gunner","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Trundle - the Troll King
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Trundle","release_date": "2010-12-01","primary_role": "jungle","secondary_role": "top","champion_type1": "fighter","champion_type2": "tank","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Trundle_0.jpg","description": "the Troll King","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Twitch - the Plague Rat
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Twitch","release_date": "2009-05-01","primary_role": "adc","secondary_role": "support","champion_type1": "marksman","champion_type2": "assassin","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Twitch_0.jpg","description": "the Plague Rat","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Urgot - the Dreadnought
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Urgot","release_date": "2010-08-24","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Urgot_0.jpg","description": "the Dreadnought","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Varus - the Arrow of Retribution
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Varus","release_date": "2012-05-08","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": "mage","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Varus_0.jpg","description": "the Arrow of Retribution","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Vi - the Piltover Enforcer
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Vi","release_date": "2012-12-19","primary_role": "jungle","secondary_role": null,"champion_type1": "fighter","champion_type2": "assassin","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Vi_0.jpg","description": "the Piltover Enforcer","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Volibear - the Relentless Storm
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Volibear","release_date": "2011-11-29","primary_role": "jungle","secondary_role": "top","champion_type1": "fighter","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Volibear_0.jpg","description": "the Relentless Storm","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Xin Zhao - the Seneschal of Demacia
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Xin Zhao","release_date": "2010-07-13","primary_role": "jungle","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/XinZhao_0.jpg","description": "the Seneschal of Demacia","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Yunara - the Unbroken Faith
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Yunara","release_date": "2025-07-16","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yunara_0.jpg","description": "the Unbroken Faith","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Zac - the Secret Weapon
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Zac","release_date": "2013-03-29","primary_role": "jungle","secondary_role": "support","champion_type1": "tank","champion_type2": "fighter","difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zac_0.jpg","description": "the Secret Weapon","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Ziggs - the Hexplosives Expert
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Ziggs","release_date": "2012-02-01","primary_role": "adc","secondary_role": "mid","champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ziggs_0.jpg","description": "the Hexplosives Expert","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Zoe - the Aspect of Twilight
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Zoe","release_date": "2017-11-21","primary_role": "mid","secondary_role": null,"champion_type1": "mage","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Zoe_0.jpg","description": "the Aspect of Twilight","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Seraphine - the Starry-Eyed Songstress
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Seraphine","release_date": "2020-10-29","primary_role": "adc","secondary_role": "support","champion_type1": "support","champion_type2": "mage","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Seraphine_0.jpg","description": "the Starry-Eyed Songstress","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Sett - the Boss
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Sett","release_date": "2020-01-14","primary_role": "top","secondary_role": null,"champion_type1": "fighter","champion_type2": "tank","difficulty": "easy","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sett_0.jpg","description": "the Boss","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Shaco - the Demon Jester
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Shaco","release_date": "2009-10-10","primary_role": "jungle","secondary_role": "support","champion_type1": "assassin","champion_type2": null,"difficulty": "hard","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Shaco_0.jpg","description": "the Demon Jester","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Shyvana - the Half-Dragon
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Shyvana","release_date": "2011-11-01","primary_role": "jungle","secondary_role": null,"champion_type1": "fighter","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Shyvana_0.jpg","description": "the Half-Dragon","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Singed - the Mad Chemist
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Singed","release_date": "2009-04-18","primary_role": "top","secondary_role": null,"champion_type1": "tank","champion_type2": "mage","difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Singed_0.jpg","description": "the Mad Chemist","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON

# Sivir - the Battle Mistress
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{"name": "Sivir","release_date": "2009-02-21","primary_role": "adc","secondary_role": null,"champion_type1": "marksman","champion_type2": null,"difficulty": "medium","strength": 70,"image_path": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Sivir_0.jpg","description": "the Battle Mistress","win_rate": null,"pick_rate": null,"ban_rate": null}
JSON
