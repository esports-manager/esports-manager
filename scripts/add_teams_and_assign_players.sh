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

echo "Teams, players, and contracts created successfully!"
