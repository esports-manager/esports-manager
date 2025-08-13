#!/bin/bash

echo "Creating Teams and Assigning Players..."

# Create T1 team
T1_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "T1",
  "nationality": "South Korea",
  "region": "LCK",
  "description": "The most successful organization in League of Legends history, with multiple World Championship titles.",
  "logo_path": "T1.webp",
  "banner_path": "T1_Banner.jpg"
}' | jq -r '.id')

echo "Created T1 team with ID: $T1_TEAM_ID"

# Create G2 Esports team
G2_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "G2 Esports",
  "nationality": "Europe",
  "region": "LEC",
  "description": "One of the most dominant teams in European League of Legends, known for innovative strategies and strong individual players.",
  "logo_path": "G2.webp",
  "banner_path": "G2_Banner.jpg"
}' | jq -r '.id')

echo "Created G2 Esports team with ID: $G2_TEAM_ID"

# Create Hanwha Life Esports team
HLE_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Hanwha Life Esports",
  "nationality": "South Korea",
  "region": "LCK",
  "description": "Korean team competing in the LCK, backed by the financial group Hanwha Life Insurance.",
  "logo_path": "HLE.webp",
  "banner_path": "HLE_Banner.jpg"
}' | jq -r '.id')

echo "Created Hanwha Life Esports team with ID: $HLE_TEAM_ID"

# Create Cloud9 team
C9_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Cloud9",
  "nationality": "United States",
  "region": "LCS",
  "description": "North American esports organization known for consistent performances across multiple games including League of Legends.",
  "logo_path": "C9.webp",
  "banner_path": "C9_Banner.jpg"
}' | jq -r '.id')

echo "Created Cloud9 team with ID: $C9_TEAM_ID"

# Create FunPlus Phoenix team
FPX_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "FunPlus Phoenix",
  "nationality": "China",
  "region": "LPL",
  "description": "Chinese team that won the 2019 World Championship, known for their aggressive playstyle.",
  "logo_path": "FPX.webp",
  "banner_path": "FPX_Banner.jpg"
}' | jq -r '.id')

echo "Created FunPlus Phoenix team with ID: $FPX_TEAM_ID"

# Create Gen.G team
GENG_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Gen.G",
  "nationality": "South Korea",
  "region": "LCK",
  "description": "Korean powerhouse known for consistent top finishes and strong macro play.",
  "logo_path": "GenG.webp",
  "banner_path": "GenG_Banner.jpg"
}' | jq -r '.id')

echo "Created Gen.G team with ID: $GENG_TEAM_ID"

# Create JD Gaming team
JDG_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "JD Gaming",
  "nationality": "China",
  "region": "LPL",
  "description": "Top LPL team with international pedigree and aggressive skirmishing style.",
  "logo_path": "JDG.webp",
  "banner_path": "JDG_Banner.jpg"
}' | jq -r '.id')

echo "Created JD Gaming team with ID: $JDG_TEAM_ID"

# Create Fnatic team
FNC_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Fnatic",
  "nationality": "Europe",
  "region": "LEC",
  "description": "Historic European organization and Worlds finalist with strong fanbase.",
  "logo_path": "FNC.webp",
  "banner_path": "FNC_Banner.jpg"
}' | jq -r '.id')

echo "Created Fnatic team with ID: $FNC_TEAM_ID"

# Create Team Liquid
TL_TEAM_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/teams/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Team Liquid",
  "nationality": "United States",
  "region": "LCS",
  "description": "North American organization with multiple domestic titles and strong infrastructure.",
  "logo_path": "TL.webp",
  "banner_path": "TL_Banner.jpg"
}' | jq -r '.id')

echo "Created Team Liquid with ID: $TL_TEAM_ID"

echo "Getting player IDs for team assignments..."

# Get Faker ID (assuming already added by add_players_data.sh)
FAKER_ID=$(curl -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Sang-hyeok",
  "last_name": "Lee",
  "date_of_birth": "1996-05-07",
  "nick_name": "Faker",
  "nationality": "South Korea",
  "bio": "Widely considered the greatest League of Legends player of all time. Three-time World Champion and T1 mid laner known for his mechanical prowess and game sense.",
  "image_path": "Faker.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 98,
  "knowledge": 99,
  "agility": 95,
  "reflexes": 97,
  "accuracy": 96,
  "aggressiveness": 85,
  "vision": 94,
  "farming": 92,
  "communication": 90,
  "morale": 95,
  "form": 93,
  "value": 15000000
}' | jq -r '.id')

# Get Caps ID (assuming already added by add_players_data.sh)
CAPS_ID=$(curl -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Rasmus",
  "last_name": "Winther",
  "date_of_birth": "1999-11-17",
  "nick_name": "Caps",
  "nationality": "Denmark",
  "bio": "Danish mid laner for G2 Esports, known for his aggressive playstyle and clutch performances. Multiple-time LEC champion and MSI winner.",
  "image_path": "Caps.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 94,
  "knowledge": 91,
  "agility": 96,
  "reflexes": 93,
  "accuracy": 89,
  "aggressiveness": 97,
  "vision": 88,
  "farming": 87,
  "communication": 86,
  "morale": 92,
  "form": 90,
  "value": 8500000
}' | jq -r '.id')

# Get other player IDs or create players if needed
# Let's create some new players for demonstration

# Creating Zeus (T1 top laner)
ZEUS_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Woo-je",
  "last_name": "Choi",
  "date_of_birth": "2004-01-31",
  "nick_name": "Zeus",
  "nationality": "South Korea",
  "bio": "Young talented top laner for T1, known for his mechanical skill and champion pool.",
  "image_path": "Zeus.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 94,
  "knowledge": 89,
  "agility": 92,
  "reflexes": 93,
  "accuracy": 90,
  "aggressiveness": 91,
  "vision": 87,
  "farming": 92,
  "communication": 85,
  "morale": 90,
  "form": 92,
  "value": 9000000
}' | jq -r '.id')

echo "Created/Retrieved Zeus with ID: $ZEUS_ID"

# Create Oner (T1 jungler)
ONER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Hyeon-joon",
  "last_name": "Moon",
  "date_of_birth": "2002-12-24",
  "nick_name": "Oner",
  "nationality": "South Korea",
  "bio": "Jungler for T1, known for his aggressive early game and smart pathing.",
  "image_path": "Oner.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 90,
  "agility": 93,
  "reflexes": 91,
  "accuracy": 89,
  "aggressiveness": 94,
  "vision": 88,
  "farming": 91,
  "communication": 89,
  "morale": 90,
  "form": 92,
  "value": 8500000
}' | jq -r '.id')

echo "Created/Retrieved Oner with ID: $ONER_ID"

# Create Gumayusi (T1 ADC)
GUMAYUSI_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Min-hyeong",
  "last_name": "Lee",
  "date_of_birth": "2002-02-06",
  "nick_name": "Gumayusi",
  "nationality": "South Korea",
  "bio": "ADC player for T1, known for his mechanical skill and laning phase.",
  "image_path": "Gumayusi.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 93,
  "knowledge": 87,
  "agility": 91,
  "reflexes": 94,
  "accuracy": 95,
  "aggressiveness": 89,
  "vision": 85,
  "farming": 94,
  "communication": 86,
  "morale": 88,
  "form": 90,
  "value": 8800000
}' | jq -r '.id')

echo "Created/Retrieved Gumayusi with ID: $GUMAYUSI_ID"

# Create Keria (T1 support)
KERIA_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Min-seok",
  "last_name": "Ryu",
  "date_of_birth": "2002-10-14",
  "nick_name": "Keria",
  "nationality": "South Korea",
  "bio": "Support player for T1, known for his playmaking ability and wide champion pool.",
  "image_path": "Keria.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 94,
  "knowledge": 92,
  "agility": 90,
  "reflexes": 93,
  "accuracy": 91,
  "aggressiveness": 88,
  "vision": 95,
  "farming": 80,
  "communication": 93,
  "morale": 91,
  "form": 92,
  "value": 9200000
}' | jq -r '.id')

echo "Created/Retrieved Keria with ID: $KERIA_ID"

# Create BrokenBlade (G2 top laner)
BROKENBLADE_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Sergen",
  "last_name": "Çelik",
  "date_of_birth": "2000-01-19",
  "nick_name": "BrokenBlade",
  "nationality": "Germany",
  "bio": "Turkish-German top laner for G2 Esports, known for his carry performances and flexibility.",
  "image_path": "BrokenBlade.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 91,
  "knowledge": 88,
  "agility": 89,
  "reflexes": 90,
  "accuracy": 87,
  "aggressiveness": 92,
  "vision": 85,
  "farming": 88,
  "communication": 90,
  "morale": 89,
  "form": 90,
  "value": 7500000
}' | jq -r '.id')

echo "Created/Retrieved BrokenBlade with ID: $BROKENBLADE_ID"

# Create Yike (G2 jungler)
YIKE_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Martin",
  "last_name": "Sundelin",
  "date_of_birth": "2001-07-26",
  "nick_name": "Yike",
  "nationality": "Sweden",
  "bio": "Swedish jungler for G2 Esports, known for his aggressive early game.",
  "image_path": "Yike.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 89,
  "knowledge": 87,
  "agility": 91,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 93,
  "vision": 88,
  "farming": 87,
  "communication": 90,
  "morale": 89,
  "form": 88,
  "value": 7000000
}' | jq -r '.id')

echo "Created/Retrieved Yike with ID: $YIKE_ID"

# Create Hans Sama (G2 ADC)
HANSSAMA_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Steven",
  "last_name": "Liv",
  "date_of_birth": "1999-09-02",
  "nick_name": "Hans Sama",
  "nationality": "France",
  "bio": "French ADC player for G2 Esports, known for his positioning and teamfight prowess.",
  "image_path": "HansSama.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 89,
  "agility": 90,
  "reflexes": 92,
  "accuracy": 93,
  "aggressiveness": 85,
  "vision": 88,
  "farming": 93,
  "communication": 87,
  "morale": 90,
  "form": 91,
  "value": 8000000
}' | jq -r '.id')

echo "Created/Retrieved Hans Sama with ID: $HANSSAMA_ID"

# Create Mikyx (G2 support)
MIKYX_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Mihael",
  "last_name": "Mehle",
  "date_of_birth": "1998-11-02",
  "nick_name": "Mikyx",
  "nationality": "Slovenia",
  "bio": "Slovenian support player for G2 Esports, known for his mechanics and playmaking ability.",
  "image_path": "Mikyx.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 90,
  "agility": 91,
  "reflexes": 93,
  "accuracy": 89,
  "aggressiveness": 88,
  "vision": 94,
  "farming": 82,
  "communication": 91,
  "morale": 90,
  "form": 91,
  "value": 7800000
}' | jq -r '.id')

echo "Created/Retrieved Mikyx with ID: $MIKYX_ID"

# Create Hanwha Life Esports roster
# Kingen (top)
KINGEN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Hyeon-gyu",
  "last_name": "Hwang",
  "date_of_birth": "1999-03-11",
  "nick_name": "Kingen",
  "nationality": "South Korea",
  "bio": "Top laner known for solid laning and teamfight presence.",
  "image_path": "Kingen.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 87,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 85,
  "aggressiveness": 86,
  "vision": 84,
  "farming": 88,
  "communication": 86,
  "morale": 88,
  "form": 87,
  "value": 5200000
}' | jq -r '.id')

# Clid (jungle)
CLID_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Tae-min",
  "last_name": "Kim",
  "date_of_birth": "1999-07-23",
  "nick_name": "Clid",
  "nationality": "South Korea",
  "bio": "Veteran jungler with strong early game pathing.",
  "image_path": "Clid.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 86,
  "knowledge": 89,
  "agility": 87,
  "reflexes": 86,
  "accuracy": 84,
  "aggressiveness": 88,
  "vision": 88,
  "farming": 85,
  "communication": 87,
  "morale": 86,
  "form": 85,
  "value": 4800000
}' | jq -r '.id')

# Zeka (mid)
ZEKA_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Geon-woo",
  "last_name": "Kim",
  "date_of_birth": "2002-11-27",
  "nick_name": "Zeka",
  "nationality": "South Korea",
  "bio": "Explosive mid laner with strong skirmishing.",
  "image_path": "Zeka.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 88,
  "agility": 90,
  "reflexes": 90,
  "accuracy": 88,
  "aggressiveness": 90,
  "vision": 86,
  "farming": 87,
  "communication": 84,
  "morale": 88,
  "form": 89,
  "value": 7000000
}' | jq -r '.id')

# Viper (adc)
VIPER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Dae-yeol",
  "last_name": "Park",
  "date_of_birth": "2000-10-19",
  "nick_name": "Viper",
  "nationality": "South Korea",
  "bio": "World-class ADC known for mechanics and teamfighting.",
  "image_path": "Viper.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 94,
  "knowledge": 90,
  "agility": 92,
  "reflexes": 94,
  "accuracy": 95,
  "aggressiveness": 88,
  "vision": 87,
  "farming": 94,
  "communication": 86,
  "morale": 90,
  "form": 92,
  "value": 9000000
}' | jq -r '.id')

# Life (support)
LIFE_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Seung-hyeon",
  "last_name": "Kim",
  "date_of_birth": "2000-04-09",
  "nick_name": "Life",
  "nationality": "South Korea",
  "bio": "Support with strong engage sense and vision control.",
  "image_path": "Life.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 90,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 86,
  "vision": 93,
  "farming": 78,
  "communication": 90,
  "morale": 89,
  "form": 88,
  "value": 5400000
}' | jq -r '.id')

# Create Cloud9 roster
# Fudge (top)
FUDGE_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Ibrahim",
  "last_name": "Allami",
  "date_of_birth": "2002-05-23",
  "nick_name": "Fudge",
  "nationality": "Australia",
  "bio": "Versatile top laner for Cloud9.",
  "image_path": "Fudge.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 89,
  "agility": 87,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 87,
  "vision": 85,
  "farming": 90,
  "communication": 88,
  "morale": 88,
  "form": 89,
  "value": 6000000
}' | jq -r '.id')

# Blaber (jungle)
BLABER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Robert",
  "last_name": "Huang",
  "date_of_birth": "2000-01-07",
  "nick_name": "Blaber",
  "nationality": "United States",
  "bio": "Aggressive NA jungler with strong skirmish sense.",
  "image_path": "Blaber.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 88,
  "agility": 90,
  "reflexes": 90,
  "accuracy": 88,
  "aggressiveness": 92,
  "vision": 86,
  "farming": 86,
  "communication": 87,
  "morale": 88,
  "form": 90,
  "value": 6800000
}' | jq -r '.id')

# Jensen (mid)
JENSEN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Nicolai",
  "last_name": "Jensen",
  "date_of_birth": "1995-01-01",
  "nick_name": "Jensen",
  "nationality": "Denmark",
  "bio": "Veteran mid laner with control mage prowess.",
  "image_path": "Jensen.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 89,
  "knowledge": 92,
  "agility": 86,
  "reflexes": 87,
  "accuracy": 88,
  "aggressiveness": 84,
  "vision": 89,
  "farming": 88,
  "communication": 90,
  "morale": 90,
  "form": 88,
  "value": 6500000
}' | jq -r '.id')

# Berserker (adc)
BERSERKER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Min-cheol",
  "last_name": "Kim",
  "date_of_birth": "2003-06-29",
  "nick_name": "Berserker",
  "nationality": "South Korea",
  "bio": "Star ADC for Cloud9 with carry potential.",
  "image_path": "Berserker.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 93,
  "knowledge": 88,
  "agility": 92,
  "reflexes": 93,
  "accuracy": 94,
  "aggressiveness": 90,
  "vision": 85,
  "farming": 93,
  "communication": 85,
  "morale": 90,
  "form": 92,
  "value": 8800000
}' | jq -r '.id')

# Vulcan (support)
VULCAN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Philippe",
  "last_name": "Laflamme",
  "date_of_birth": "1999-04-28",
  "nick_name": "Vulcan",
  "nationality": "Canada",
  "bio": "Support with strong laning and roaming sense.",
  "image_path": "Vulcan.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 90,
  "agility": 88,
  "reflexes": 90,
  "accuracy": 86,
  "aggressiveness": 86,
  "vision": 94,
  "farming": 80,
  "communication": 92,
  "morale": 90,
  "form": 90,
  "value": 7000000
}' | jq -r '.id')

# Create FPX roster
# GimGoon (top)
GIMGOON_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Han-saem",
  "last_name": "Kim",
  "date_of_birth": "1996-07-28",
  "nick_name": "GimGoon",
  "nationality": "South Korea",
  "bio": "Veteran top laner and 2019 World Champion.",
  "image_path": "GimGoon.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 85,
  "knowledge": 90,
  "agility": 82,
  "reflexes": 84,
  "accuracy": 83,
  "aggressiveness": 82,
  "vision": 88,
  "farming": 86,
  "communication": 88,
  "morale": 87,
  "form": 84,
  "value": 4000000
}' | jq -r '.id')

# Tian (jungle)
TIAN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Liang",
  "last_name": "Gao",
  "date_of_birth": "2000-05-24",
  "nick_name": "Tian",
  "nationality": "China",
  "bio": "World Champion jungler known for clutch plays.",
  "image_path": "Tian.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 89,
  "agility": 90,
  "reflexes": 90,
  "accuracy": 88,
  "aggressiveness": 92,
  "vision": 86,
  "farming": 85,
  "communication": 86,
  "morale": 88,
  "form": 88,
  "value": 7200000
}' | jq -r '.id')

# Doinb (mid)
DOINB_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Tae-sang",
  "last_name": "Kim",
  "date_of_birth": "1996-12-30",
  "nick_name": "Doinb",
  "nationality": "South Korea",
  "bio": "Unique mid laner with innovative picks and macro.",
  "image_path": "Doinb.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 94,
  "agility": 84,
  "reflexes": 86,
  "accuracy": 86,
  "aggressiveness": 84,
  "vision": 92,
  "farming": 86,
  "communication": 92,
  "morale": 90,
  "form": 86,
  "value": 6500000
}' | jq -r '.id')

# Lwx (adc)
LWX_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Han",
  "last_name": "Lin",
  "date_of_birth": "1998-11-08",
  "nick_name": "Lwx",
  "nationality": "China",
  "bio": "ADC carry for FPX.",
  "image_path": "Lwx.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 87,
  "agility": 90,
  "reflexes": 92,
  "accuracy": 92,
  "aggressiveness": 88,
  "vision": 84,
  "farming": 92,
  "communication": 84,
  "morale": 88,
  "form": 89,
  "value": 7000000
}' | jq -r '.id')

# Crisp (support)
CRISP_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Ke",
  "last_name": "Liu",
  "date_of_birth": "1999-04-22",
  "nick_name": "Crisp",
  "nationality": "China",
  "bio": "Support with elite vision control and peel.",
  "image_path": "Crisp.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 91,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 85,
  "aggressiveness": 84,
  "vision": 94,
  "farming": 78,
  "communication": 90,
  "morale": 89,
  "form": 88,
  "value": 6000000
}' | jq -r '.id')

# Create Gen.G roster
# Doran (top)
DORAN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Chan-hyeok",
  "last_name": "Choi",
  "date_of_birth": "2000-06-22",
  "nick_name": "Doran",
  "nationality": "South Korea",
  "bio": "Stable top laner for Gen.G.",
  "image_path": "Doran.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 89,
  "agility": 86,
  "reflexes": 87,
  "accuracy": 85,
  "aggressiveness": 84,
  "vision": 86,
  "farming": 88,
  "communication": 88,
  "morale": 88,
  "form": 87,
  "value": 5600000
}' | jq -r '.id')

# Peanut (jungle)
PEANUT_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Han",
  "last_name": "Wang-ho",
  "date_of_birth": "1998-02-03",
  "nick_name": "Peanut",
  "nationality": "South Korea",
  "bio": "Veteran jungler with proactive playmaking.",
  "image_path": "Peanut.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 89,
  "knowledge": 92,
  "agility": 88,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 90,
  "vision": 90,
  "farming": 86,
  "communication": 92,
  "morale": 90,
  "form": 89,
  "value": 7000000
}' | jq -r '.id')

# Chovy (mid)
CHOVY_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Jeong-hoon",
  "last_name": "Jeong",
  "date_of_birth": "2001-03-03",
  "nick_name": "Chovy",
  "nationality": "South Korea",
  "bio": "Elite mid laner known for laning dominance.",
  "image_path": "Chovy.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 95,
  "knowledge": 93,
  "agility": 92,
  "reflexes": 93,
  "accuracy": 92,
  "aggressiveness": 88,
  "vision": 90,
  "farming": 95,
  "communication": 86,
  "morale": 92,
  "form": 94,
  "value": 12000000
}' | jq -r '.id')

# Peyz (adc)
PEYZ_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Ji-woo",
  "last_name": "Kim",
  "date_of_birth": "2006-01-06",
  "nick_name": "Peyz",
  "nationality": "South Korea",
  "bio": "Young ADC talent with carry potential.",
  "image_path": "Peyz.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 88,
  "agility": 92,
  "reflexes": 93,
  "accuracy": 92,
  "aggressiveness": 90,
  "vision": 85,
  "farming": 93,
  "communication": 84,
  "morale": 90,
  "form": 92,
  "value": 8000000
}' | jq -r '.id')

# Delight (support)
DELIGHT_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "You",
  "last_name": "Hyeon-joon",
  "date_of_birth": "2001-11-20",
  "nick_name": "Delight",
  "nationality": "South Korea",
  "bio": "Support with playmaking instincts.",
  "image_path": "Delight.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 90,
  "agility": 87,
  "reflexes": 89,
  "accuracy": 86,
  "aggressiveness": 85,
  "vision": 93,
  "farming": 78,
  "communication": 90,
  "morale": 90,
  "form": 88,
  "value": 6200000
}' | jq -r '.id')

# Create JDG roster
# 369 (top)
THREESIXNINE_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Qi",
  "last_name": "Bai",
  "date_of_birth": "1999-07-12",
  "nick_name": "369",
  "nationality": "China",
  "bio": "Dominant top laner for JDG.",
  "image_path": "369.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 90,
  "agility": 90,
  "reflexes": 92,
  "accuracy": 90,
  "aggressiveness": 90,
  "vision": 86,
  "farming": 91,
  "communication": 84,
  "morale": 90,
  "form": 92,
  "value": 9500000
}' | jq -r '.id')

# Kanavi (jungle)
KANAVI_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Jin-hyeok",
  "last_name": "Seo",
  "date_of_birth": "2000-11-02",
  "nick_name": "Kanavi",
  "nationality": "South Korea",
  "bio": "Carry jungler with strong farming and teamfights.",
  "image_path": "Kanavi.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 90,
  "agility": 90,
  "reflexes": 90,
  "accuracy": 89,
  "aggressiveness": 90,
  "vision": 86,
  "farming": 92,
  "communication": 86,
  "morale": 90,
  "form": 92,
  "value": 9800000
}' | jq -r '.id')

# Knight (mid)
KNIGHT_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Ding",
  "last_name": "Zhuo",
  "date_of_birth": "2000-05-22",
  "nick_name": "Knight",
  "nationality": "China",
  "bio": "Mechanical mid laner with highlight plays.",
  "image_path": "Knight.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 95,
  "knowledge": 90,
  "agility": 94,
  "reflexes": 95,
  "accuracy": 93,
  "aggressiveness": 92,
  "vision": 86,
  "farming": 90,
  "communication": 84,
  "morale": 90,
  "form": 93,
  "value": 11000000
}' | jq -r '.id')

# Ruler (adc)
RULER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Jae-hyuk",
  "last_name": "Park",
  "date_of_birth": "1998-12-29",
  "nick_name": "Ruler",
  "nationality": "South Korea",
  "bio": "World-class ADC and World Champion.",
  "image_path": "Ruler.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 95,
  "knowledge": 92,
  "agility": 93,
  "reflexes": 95,
  "accuracy": 95,
  "aggressiveness": 90,
  "vision": 90,
  "farming": 95,
  "communication": 86,
  "morale": 92,
  "form": 94,
  "value": 13000000
}' | jq -r '.id')

# Missing (support)
MISSING_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Liang",
  "last_name": "Lou",
  "date_of_birth": "2001-05-08",
  "nick_name": "Missing",
  "nationality": "China",
  "bio": "Support with solid fundamentals and engage.",
  "image_path": "Missing.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 90,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 86,
  "vision": 92,
  "farming": 78,
  "communication": 90,
  "morale": 89,
  "form": 88,
  "value": 6200000
}' | jq -r '.id')

# Create Fnatic roster
# Wunder (top)
WUNDER_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Martin",
  "last_name": "Hansen",
  "date_of_birth": "1998-11-09",
  "nick_name": "Wunder",
  "nationality": "Denmark",
  "bio": "Experienced top laner with flexible pool.",
  "image_path": "Wunder.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 87,
  "knowledge": 90,
  "agility": 86,
  "reflexes": 86,
  "accuracy": 85,
  "aggressiveness": 84,
  "vision": 86,
  "farming": 88,
  "communication": 90,
  "morale": 88,
  "form": 86,
  "value": 5200000
}' | jq -r '.id')

# Razork (jungle)
RAZORK_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Iván",
  "last_name": "Martín",
  "date_of_birth": "2000-10-06",
  "nick_name": "Razork",
  "nationality": "Spain",
  "bio": "Proactive EU jungler.",
  "image_path": "Razork.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 89,
  "agility": 88,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 90,
  "vision": 86,
  "farming": 85,
  "communication": 88,
  "morale": 88,
  "form": 88,
  "value": 6000000
}' | jq -r '.id')

# Humanoid (mid)
HUMANOID_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Marek",
  "last_name": "Brázda",
  "date_of_birth": "2000-03-07",
  "nick_name": "Humanoid",
  "nationality": "Czech Republic",
  "bio": "Mid laner with great teamfight impact.",
  "image_path": "Humanoid.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 90,
  "agility": 89,
  "reflexes": 90,
  "accuracy": 88,
  "aggressiveness": 88,
  "vision": 88,
  "farming": 88,
  "communication": 88,
  "morale": 90,
  "form": 90,
  "value": 8000000
}' | jq -r '.id')

# Upset (adc)
UPSET_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Elias",
  "last_name": "Lipp",
  "date_of_birth": "1999-12-16",
  "nick_name": "Upset",
  "nationality": "Germany",
  "bio": "EU ADC with elite laning.",
  "image_path": "Upset.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 92,
  "knowledge": 90,
  "agility": 91,
  "reflexes": 92,
  "accuracy": 93,
  "aggressiveness": 88,
  "vision": 86,
  "farming": 93,
  "communication": 86,
  "morale": 90,
  "form": 92,
  "value": 9000000
}' | jq -r '.id')

# Hylissang (support)
HYLISSANG_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Zdravets",
  "last_name": "Iliev Galabov",
  "date_of_birth": "1995-03-30",
  "nick_name": "Hylissang",
  "nationality": "Bulgaria",
  "bio": "Playmaking support with engage focus.",
  "image_path": "Hylissang.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 90,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 90,
  "vision": 92,
  "farming": 78,
  "communication": 90,
  "morale": 88,
  "form": 88,
  "value": 6200000
}' | jq -r '.id')

# Create Team Liquid roster
# Impact (top)
IMPACT_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Eon-yeong",
  "last_name": "Jeong",
  "date_of_birth": "1995-03-07",
  "nick_name": "Impact",
  "nationality": "South Korea",
  "bio": "World Champion top laner with veteran presence.",
  "image_path": "Impact.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 92,
  "agility": 86,
  "reflexes": 86,
  "accuracy": 86,
  "aggressiveness": 84,
  "vision": 90,
  "farming": 88,
  "communication": 92,
  "morale": 90,
  "form": 88,
  "value": 6500000
}' | jq -r '.id')

# Santorin (jungle)
SANTORIN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Lucas",
  "last_name": "Tao Kilmer Larsen",
  "date_of_birth": "1997-05-06",
  "nick_name": "Santorin",
  "nationality": "Denmark",
  "bio": "Steady jungler with objective focus.",
  "image_path": "Santorin.webp",
  "role": "jungle",
  "is_active": true,
  "mechanics": 86,
  "knowledge": 90,
  "agility": 86,
  "reflexes": 86,
  "accuracy": 86,
  "aggressiveness": 84,
  "vision": 90,
  "farming": 85,
  "communication": 90,
  "morale": 88,
  "form": 86,
  "value": 5200000
}' | jq -r '.id')

# Bjergsen (mid)
BJERGSEN_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Søren",
  "last_name": "Bjerg",
  "date_of_birth": "1996-02-21",
  "nick_name": "Bjergsen",
  "nationality": "Denmark",
  "bio": "NA mid lane legend.",
  "image_path": "Bjergsen.webp",
  "role": "mid",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 95,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 88,
  "aggressiveness": 84,
  "vision": 92,
  "farming": 88,
  "communication": 94,
  "morale": 92,
  "form": 88,
  "value": 9000000
}' | jq -r '.id')

# Hans sama moved earlier; use CoreJJ (support) and Yeon (adc)
# Yeon (adc)
YEON_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Sean",
  "last_name": "Sung",
  "date_of_birth": "2003-06-22",
  "nick_name": "Yeon",
  "nationality": "United States",
  "bio": "Young ADC talent for TL.",
  "image_path": "Yeon.webp",
  "role": "adc",
  "is_active": true,
  "mechanics": 90,
  "knowledge": 86,
  "agility": 90,
  "reflexes": 92,
  "accuracy": 92,
  "aggressiveness": 88,
  "vision": 84,
  "farming": 92,
  "communication": 84,
  "morale": 88,
  "form": 90,
  "value": 7000000
}' | jq -r '.id')

# CoreJJ (support)
COREJJ_ID=$(curl -s -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Min-seok",
  "last_name": "Jo",
  "date_of_birth": "1994-06-22",
  "nick_name": "CoreJJ",
  "nationality": "South Korea",
  "bio": "World Champion support known for shotcalling.",
  "image_path": "CoreJJ.webp",
  "role": "support",
  "is_active": true,
  "mechanics": 88,
  "knowledge": 95,
  "agility": 86,
  "reflexes": 88,
  "accuracy": 86,
  "aggressiveness": 84,
  "vision": 95,
  "farming": 78,
  "communication": 96,
  "morale": 92,
  "form": 88,
  "value": 8500000
}' | jq -r '.id')

echo "Creating player contracts..."

# Current date and contract end dates
CURRENT_DATE=$(date +"%Y-%m-%d")
NEXT_YEAR=$(date -d "+1 year" +"%Y-%m-%d")
TWO_YEARS=$(date -d "+2 years" +"%Y-%m-%d")

# Create contracts for T1 players
echo "Creating T1 player contracts..."

# Faker to T1
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 2500000,
  \"is_active\": true,
  \"team_id\": $T1_TEAM_ID,
  \"player_id\": $FAKER_ID
  }
}"

# Zeus to T1
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1800000,
  \"is_active\": true,
  \"team_id\": $T1_TEAM_ID,
  \"player_id\": $ZEUS_ID
  }
}"

# Oner to T1
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1700000,
  \"is_active\": true,
  \"team_id\": $T1_TEAM_ID,
  \"player_id\": $ONER_ID
  }
}"

# Gumayusi to T1
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1750000,
  \"is_active\": true,
  \"team_id\": $T1_TEAM_ID,
  \"player_id\": $GUMAYUSI_ID
  }
}"

# Keria to T1
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1850000,
  \"is_active\": true,
  \"team_id\": $T1_TEAM_ID,
  \"player_id\": $KERIA_ID
  }
}"

# Create contracts for G2 players
echo "Creating G2 player contracts..."

# Caps to G2
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 2200000,
  \"is_active\": true,
  \"team_id\": $G2_TEAM_ID,
  \"player_id\": $CAPS_ID
  }
}"

# BrokenBlade to G2
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1500000,
  \"is_active\": true,
  \"team_id\": $G2_TEAM_ID,
  \"player_id\": $BROKENBLADE_ID
  }
}"

# Yike to G2
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $G2_TEAM_ID,
  \"player_id\": $YIKE_ID
  }
}"

# Hans Sama to G2
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1600000,
  \"is_active\": true,
  \"team_id\": $G2_TEAM_ID,
  \"player_id\": $HANSSAMA_ID
  }
}"

# Mikyx to G2
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1550000,
  \"is_active\": true,
  \"team_id\": $G2_TEAM_ID,
  \"player_id\": $MIKYX_ID
  }
}"

# Create contracts for Hanwha Life Esports players
echo "Creating HLE player contracts..."

# Kingen to HLE
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 900000,
  \"is_active\": true,
  \"team_id\": $HLE_TEAM_ID,
  \"player_id\": $KINGEN_ID
  }
}"

# Clid to HLE
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 850000,
  \"is_active\": true,
  \"team_id\": $HLE_TEAM_ID,
  \"player_id\": $CLID_ID
  }
}"

# Zeka to HLE
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $HLE_TEAM_ID,
  \"player_id\": $ZEKA_ID
  }
}"

# Viper to HLE
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1700000,
  \"is_active\": true,
  \"team_id\": $HLE_TEAM_ID,
  \"player_id\": $VIPER_ID
  }
}"

# Life to HLE
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 800000,
  \"is_active\": true,
  \"team_id\": $HLE_TEAM_ID,
  \"player_id\": $LIFE_ID
  }
}"

# Create contracts for Cloud9 players
echo "Creating Cloud9 player contracts..."

# Fudge to C9
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1200000,
  \"is_active\": true,
  \"team_id\": $C9_TEAM_ID,
  \"player_id\": $FUDGE_ID
  }
}"

# Blaber to C9
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1300000,
  \"is_active\": true,
  \"team_id\": $C9_TEAM_ID,
  \"player_id\": $BLABER_ID
  }
}"

# Jensen to C9
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $C9_TEAM_ID,
  \"player_id\": $JENSEN_ID
  }
}"

# Berserker to C9
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1500000,
  \"is_active\": true,
  \"team_id\": $C9_TEAM_ID,
  \"player_id\": $BERSERKER_ID
  }
}"

# Vulcan to C9
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1100000,
  \"is_active\": true,
  \"team_id\": $C9_TEAM_ID,
  \"player_id\": $VULCAN_ID
  }
}"

# Create contracts for FPX players
echo "Creating FPX player contracts..."

# GimGoon to FPX
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 800000,
  \"is_active\": true,
  \"team_id\": $FPX_TEAM_ID,
  \"player_id\": $GIMGOON_ID
  }
}"

# Tian to FPX
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $FPX_TEAM_ID,
  \"player_id\": $TIAN_ID
  }
}"

# Doinb to FPX
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1500000,
  \"is_active\": true,
  \"team_id\": $FPX_TEAM_ID,
  \"player_id\": $DOINB_ID
  }
}"

# Lwx to FPX
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1200000,
  \"is_active\": true,
  \"team_id\": $FPX_TEAM_ID,
  \"player_id\": $LWX_ID
  }
}"

# Crisp to FPX
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 900000,
  \"is_active\": true,
  \"team_id\": $FPX_TEAM_ID,
  \"player_id\": $CRISP_ID
  }
}"

# Create contracts for Gen.G players
echo "Creating Gen.G player contracts..."

# Doran to Gen.G
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1100000,
  \"is_active\": true,
  \"team_id\": $GENG_TEAM_ID,
  \"player_id\": $DORAN_ID
  }
}"

# Peanut to Gen.G
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $GENG_TEAM_ID,
  \"player_id\": $PEANUT_ID
  }
}"

# Chovy to Gen.G
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 2200000,
  \"is_active\": true,
  \"team_id\": $GENG_TEAM_ID,
  \"player_id\": $CHOVY_ID
  }
}"

# Peyz to Gen.G
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1500000,
  \"is_active\": true,
  \"team_id\": $GENG_TEAM_ID,
  \"player_id\": $PEYZ_ID
  }
}"

# Delight to Gen.G
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1000000,
  \"is_active\": true,
  \"team_id\": $GENG_TEAM_ID,
  \"player_id\": $DELIGHT_ID
  }
}"

# Create contracts for JDG players
echo "Creating JD Gaming player contracts..."

# 369 to JDG
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1500000,
  \"is_active\": true,
  \"team_id\": $JDG_TEAM_ID,
  \"player_id\": $THREESIXNINE_ID
  }
}"

# Kanavi to JDG
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1700000,
  \"is_active\": true,
  \"team_id\": $JDG_TEAM_ID,
  \"player_id\": $KANAVI_ID
  }
}"

# Knight to JDG
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 2100000,
  \"is_active\": true,
  \"team_id\": $JDG_TEAM_ID,
  \"player_id\": $KNIGHT_ID
  }
}"

# Ruler to JDG
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 2300000,
  \"is_active\": true,
  \"team_id\": $JDG_TEAM_ID,
  \"player_id\": $RULER_ID
  }
}"

# Missing to JDG
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1000000,
  \"is_active\": true,
  \"team_id\": $JDG_TEAM_ID,
  \"player_id\": $MISSING_ID
  }
}"

# Create contracts for Fnatic players
echo "Creating Fnatic player contracts..."

# Wunder to FNC
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 900000,
  \"is_active\": true,
  \"team_id\": $FNC_TEAM_ID,
  \"player_id\": $WUNDER_ID
  }
}"

# Razork to FNC
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 950000,
  \"is_active\": true,
  \"team_id\": $FNC_TEAM_ID,
  \"player_id\": $RAZORK_ID
  }
}"

# Humanoid to FNC
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1400000,
  \"is_active\": true,
  \"team_id\": $FNC_TEAM_ID,
  \"player_id\": $HUMANOID_ID
  }
}"

# Upset to FNC
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1600000,
  \"is_active\": true,
  \"team_id\": $FNC_TEAM_ID,
  \"player_id\": $UPSET_ID
  }
}"

# Hylissang to FNC
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 850000,
  \"is_active\": true,
  \"team_id\": $FNC_TEAM_ID,
  \"player_id\": $HYLISSANG_ID
  }
}"

# Create contracts for Team Liquid players
echo "Creating Team Liquid player contracts..."

# Impact to TL
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1200000,
  \"is_active\": true,
  \"team_id\": $TL_TEAM_ID,
  \"player_id\": $IMPACT_ID
  }
}"

# Santorin to TL
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1100000,
  \"is_active\": true,
  \"team_id\": $TL_TEAM_ID,
  \"player_id\": $SANTORIN_ID
  }
}"

# Bjergsen to TL
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$TWO_YEARS\",
  \"salary\": 1800000,
  \"is_active\": true,
  \"team_id\": $TL_TEAM_ID,
  \"player_id\": $BJERGSEN_ID
  }
}"

# Yeon to TL
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 900000,
  \"is_active\": true,
  \"team_id\": $TL_TEAM_ID,
  \"player_id\": $YEON_ID
  }
}"

# CoreJJ to TL
curl -X 'POST' \
  'http://localhost:8000/api/moba/teams/add-player/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d "{ \"contract\": {
  \"start_date\": \"$CURRENT_DATE\",
  \"end_date\": \"$NEXT_YEAR\",
  \"salary\": 1300000,
  \"is_active\": true,
  \"team_id\": $TL_TEAM_ID,
  \"player_id\": $COREJJ_ID
  }
}"

echo "Teams, players, and contracts created successfully!"
