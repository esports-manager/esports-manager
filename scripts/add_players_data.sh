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

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Min-seok",
    "last_name": "Ryu",
    "date_of_birth": "2002-10-14",
    "nick_name": "Keria",
    "nationality": "South Korea",
    "bio": "World Champion support for T1, known for his exceptional mechanics and playmaking ability. One of the most skilled support players in the world with incredible champion pool depth.",
    "image_path": "Keria.webp",
    "role": "support",
    "is_active": true,
    "mechanics": 96,
    "knowledge": 93,
    "agility": 94,
    "reflexes": 95,
    "accuracy": 93,
    "aggressiveness": 89,
    "vision": 96,
    "farming": 78,
    "communication": 92,
    "morale": 90,
    "form": 94,
    "value": 8000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Woo-je",
    "last_name": "Choi",
    "date_of_birth": "2004-01-31",
    "nick_name": "Zeus",
    "nationality": "South Korea",
    "bio": "World Champion top laner for T1 and one of the youngest players to win Worlds. Known for his exceptional laning phase, teamfighting, and versatile champion pool.",
    "image_path": "Zeus.webp",
    "role": "top",
    "is_active": true,
    "mechanics": 95,
    "knowledge": 91,
    "agility": 93,
    "reflexes": 94,
    "accuracy": 92,
    "aggressiveness": 87,
    "vision": 89,
    "farming": 94,
    "communication": 88,
    "morale": 92,
    "form": 95,
    "value": 9500000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Hyeon-jun",
    "last_name": "Moon",
    "date_of_birth": "2002-12-24",
    "nick_name": "Oner",
    "nationality": "South Korea",
    "bio": "World Champion jungler for T1, known for his solid fundamentals and team-oriented playstyle. Excellent at enabling his teammates and making crucial plays in high-pressure situations.",
    "image_path": "Oner.webp",
    "role": "jungle",
    "is_active": true,
    "mechanics": 90,
    "knowledge": 94,
    "agility": 91,
    "reflexes": 92,
    "accuracy": 89,
    "aggressiveness": 83,
    "vision": 95,
    "farming": 88,
    "communication": 93,
    "morale": 94,
    "form": 92,
    "value": 7000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Min-hyeong",
    "last_name": "Lee",
    "date_of_birth": "2002-02-06",
    "nick_name": "Gumayusi",
    "nationality": "South Korea",
    "bio": "World Champion ADC for T1, known for his exceptional laning phase and teamfighting positioning. Young prodigy with incredible mechanical skill and game sense.",
    "image_path": "Gumayusi.webp",
    "role": "adc",
    "is_active": true,
    "mechanics": 94,
    "knowledge": 89,
    "agility": 92,
    "reflexes": 93,
    "accuracy": 95,
    "aggressiveness": 85,
    "vision": 87,
    "farming": 96,
    "communication": 86,
    "morale": 90,
    "form": 93,
    "value": 8500000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Gi-in",
    "last_name": "Kim",
    "date_of_birth": "1999-12-30",
    "nick_name": "Kiin",
    "nationality": "South Korea",
    "bio": "Elite Korean top laner for Hanwha Life Esports, consistently regarded as one of the best top laners in the LCK. Known for his exceptional laning phase, teamfighting, and ability to carry games.",
    "image_path": "Kiin.webp",
    "role": "top",
    "is_active": true,
    "mechanics": 96,
    "knowledge": 93,
    "agility": 94,
    "reflexes": 95,
    "accuracy": 94,
    "aggressiveness": 88,
    "vision": 91,
    "farming": 95,
    "communication": 87,
    "morale": 89,
    "form": 93,
    "value": 9000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Si-hoon",
    "last_name": "Son",
    "date_of_birth": "1999-05-04",
    "nick_name": "Lehends",
    "nationality": "South Korea",
    "bio": "Korean support for Hanwha Life Esports, known for his aggressive playmaking style and mechanical prowess on engage supports. One of the most impactful supports in the LCK.",
    "image_path": "Lehends.webp",
    "role": "support",
    "is_active": true,
    "mechanics": 94,
    "knowledge": 91,
    "agility": 93,
    "reflexes": 94,
    "accuracy": 90,
    "aggressiveness": 95,
    "vision": 92,
    "farming": 75,
    "communication": 89,
    "morale": 88,
    "form": 91,
    "value": 6000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Su-hwan",
    "last_name": "Park",
    "date_of_birth": "2003-01-15",
    "nick_name": "Peyz",
    "nationality": "South Korea",
    "bio": "Rising Korean ADC talent for Hanwha Life Esports. Young player with exceptional mechanical skill and positioning, considered one of the most promising ADCs in the LCK.",
    "image_path": "Peyz.webp",
    "role": "adc",
    "is_active": true,
    "mechanics": 92,
    "knowledge": 85,
    "agility": 91,
    "reflexes": 93,
    "accuracy": 93,
    "aggressiveness": 82,
    "vision": 84,
    "farming": 91,
    "communication": 83,
    "morale": 87,
    "form": 89,
    "value": 5500000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jae-hyuk",
    "last_name": "Park",
    "date_of_birth": "1998-12-29",
    "nick_name": "Ruler",
    "nationality": "South Korea",
    "bio": "World Champion ADC currently playing for JD Gaming. Known for his exceptional positioning, clutch performances, and being one of the most consistent ADCs in professional League of Legends.",
    "image_path": "Ruler.webp",
    "role": "adc",
    "is_active": true,
    "mechanics": 95,
    "knowledge": 94,
    "agility": 92,
    "reflexes": 93,
    "accuracy": 97,
    "aggressiveness": 85,
    "vision": 91,
    "farming": 95,
    "communication": 89,
    "morale": 92,
    "form": 93,
    "value": 10000000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Gun-woo",
    "last_name": "Kim",
    "date_of_birth": "2002-09-12",
    "nick_name": "Duro",
    "nationality": "South Korea",
    "bio": "Korean top laner for Gen.G, known for his solid fundamentals and teamfighting ability. Reliable player who excels at playing for the team and enabling his carries.",
    "image_path": "Duro.webp",
    "role": "top",
    "is_active": true,
    "mechanics": 88,
    "knowledge": 91,
    "agility": 87,
    "reflexes": 89,
    "accuracy": 87,
    "aggressiveness": 78,
    "vision": 90,
    "farming": 89,
    "communication": 92,
    "morale": 90,
    "form": 88,
    "value": 4500000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Wang-ho",
    "last_name": "Han",
    "date_of_birth": "1998-02-03",
    "nick_name": "Peanut",
    "nationality": "South Korea",
    "bio": "Veteran Korean jungler for Gen.G with extensive international experience. Known for his aggressive early game style, jungle pathing expertise, and leadership on the team.",
    "image_path": "Peanut.webp",
    "role": "jungle",
    "is_active": true,
    "mechanics": 92,
    "knowledge": 96,
    "agility": 91,
    "reflexes": 90,
    "accuracy": 89,
    "aggressiveness": 93,
    "vision": 94,
    "farming": 91,
    "communication": 93,
    "morale": 91,
    "form": 90,
    "value": 7500000
  }'

curl -X POST http://localhost:8000/api/moba/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Heo",
    "last_name": "Su",
    "date_of_birth": "2000-07-25",
    "nick_name": "ShowMaker",
    "nationality": "South Korea",
    "bio": "World Champion mid laner for KT Rolster, known for his exceptional mechanical skill and clutch performances. Former DWG KIA player who dominated the 2020 World Championship.",
    "image_path": "ShowMaker.webp",
    "role": "mid",
    "is_active": true,
    "mechanics": 97,
    "knowledge": 93,
    "agility": 95,
    "reflexes": 96,
    "accuracy": 94,
    "aggressiveness": 91,
    "vision": 88,
    "farming": 90,
    "communication": 87,
    "morale": 89,
    "form": 91,
    "value": 11500000
  }'