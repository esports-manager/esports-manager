#!/bin/bash

curl -X 'POST' \
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
}'

curl -X 'POST' \
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
}'

curl -X 'POST' \
  'http://localhost:8000/api/moba/players/' \
  -H 'accept: application/json' \
  -H "Content-Type: application/json" \
  -d '{
  "first_name": "Mingyi",
  "last_name": "Lu",
  "date_of_birth": "2001-04-02",
  "nick_name": "Bin",
  "nationality": "China",
  "bio": "Chinese top laner for Bilibili Gaming, known for his exceptional mechanical skill and carry potential. World Champion and multiple-time LPL champion.",
  "image_path": "Bin.webp",
  "role": "top",
  "is_active": true,
  "mechanics": 96,
  "knowledge": 88,
  "agility": 94,
  "reflexes": 95,
  "accuracy": 92,
  "aggressiveness": 93,
  "vision": 85,
  "farming": 89,
  "communication": 82,
  "morale": 88,
  "form": 91,
  "value": 7500000
}'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Felipe",
    "last_name": "Gonçalves",
    "date_of_birth": "1992-06-15",
    "nick_name": "brTT",
    "nationality": "Brazil",
    "bio": "Legendary Brazilian ADC and one of the most iconic players in Brazilian League of Legends history. Known for his aggressive playstyle and mechanical skill. Former paiN Gaming and INTZ player who represented Brazil at Worlds.",
    "image_path": "brTT.webp",
    "role": "adc",
    "is_active": false,
    "mechanics": 88,
    "knowledge": 85,
    "agility": 90,
    "reflexes": 89,
    "accuracy": 91,
    "aggressiveness": 95,
    "vision": 82,
    "farming": 87,
    "communication": 80,
    "morale": 88,
    "form": 75,
    "value": 2500000
  }'


curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jeong-hyeon",
    "last_name": "Choi",
    "date_of_birth": "2001-03-03",
    "nick_name": "Chovy",
    "nationality": "South Korea",
    "bio": "Korean mid laner for Gen.G, widely regarded as one of the best laning mid laners in the world. Known for his exceptional CS numbers and mechanical precision.",
    "image_path": "Chovy.webp",
    "role": "mid",
    "is_active": true,
    "mechanics": 97,
    "knowledge": 92,
    "agility": 93,
    "reflexes": 94,
    "accuracy": 98,
    "aggressiveness": 75,
    "vision": 89,
    "farming": 99,
    "communication": 85,
    "morale": 87,
    "form": 94,
    "value": 12000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Gun-bu",
    "last_name": "Kim",
    "date_of_birth": "2001-08-18",
    "nick_name": "Canyon",
    "nationality": "South Korea",
    "bio": "World Champion jungler for T1, known for his game-changing plays and exceptional jungle pathing. One of the most impactful junglers in professional League of Legends.",
    "image_path": "Canyon.webp",
    "role": "jungle",
    "is_active": true,
    "mechanics": 95,
    "knowledge": 96,
    "agility": 94,
    "reflexes": 93,
    "accuracy": 91,
    "aggressiveness": 88,
    "vision": 98,
    "farming": 92,
    "communication": 91,
    "morale": 93,
    "form": 95,
    "value": 11000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Yiliang",
    "last_name": "Peng",
    "date_of_birth": "1993-07-19",
    "nick_name": "Doublelift",
    "nationality": "United States",
    "bio": "Legendary NA ADC and eight-time LCS champion. Known for his trash talk, clutch performances, and being one of the most successful NA players of all time.",
    "image_path": "Doublelift.webp",
    "role": "adc",
    "is_active": false,
    "mechanics": 92,
    "knowledge": 88,
    "agility": 89,
    "reflexes": 90,
    "accuracy": 94,
    "aggressiveness": 91,
    "vision": 85,
    "farming": 93,
    "communication": 87,
    "morale": 85,
    "form": 70,
    "value": 4000000
  }'


curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Seong-hwan",
    "last_name": "Kang",
    "date_of_birth": "1999-11-06",
    "nick_name": "TheShy",
    "nationality": "South Korea",
    "bio": "World Champion top laner known for his incredible mechanical skill and aggressive playstyle. Former Invictus Gaming player who made legendary plays that redefined top lane.",
    "image_path": "TheShy.webp",
    "role": "top",
    "is_active": true,
    "mechanics": 99,
    "knowledge": 85,
    "agility": 97,
    "reflexes": 96,
    "accuracy": 94,
    "aggressiveness": 98,
    "vision": 80,
    "farming": 88,
    "communication": 78,
    "morale": 82,
    "form": 86,
    "value": 6500000
  }'


curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Yong-in",
    "last_name": "Jo",
    "date_of_birth": "1994-12-03",
    "nick_name": "CoreJJ",
    "nationality": "South Korea",
    "bio": "World Champion support for Team Liquid. Former ADC turned support who became one of the best supports in the world. Known for his leadership and shot-calling.",
    "image_path": "CoreJJ.webp",
    "role": "support",
    "is_active": true,
    "mechanics": 90,
    "knowledge": 96,
    "agility": 88,
    "reflexes": 89,
    "accuracy": 92,
    "aggressiveness": 82,
    "vision": 97,
    "farming": 75,
    "communication": 95,
    "morale": 91,
    "form": 89,
    "value": 5500000
  }'