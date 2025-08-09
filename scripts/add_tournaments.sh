#!/usr/bin/env bash
# Adds sample MOBA tournaments via the public API.
# Usage: ./scripts/add_tournaments.sh [BASE_URL]
# Default BASE_URL: http://localhost:8000

set -euo pipefail

BASE_URL=${1:-http://localhost:8000}
API="$BASE_URL/api/moba/tournaments"

create_tournament() {
  local payload="$1"
  echo "Creating tournament: $(echo "$payload" | jq -r .name)"
  curl -sS -X POST "$API/" \
    -H 'Content-Type: application/json' \
    -d "$payload" | jq -r '.id, .name' >/dev/null
}

# Ensure jq is available for better output; if not, fall back silently.
if ! command -v jq >/dev/null 2>&1; then
  jq() { cat >/dev/null; }
fi

# Premier example
create_tournament '{
  "name": "Worlds Championship",
  "abbreviation": "Worlds",
  "type": "international",
  "format": "double_elimination",
  "tier": "premier",
  "start_date": "2025-10-01T00:00:00",
  "end_date": "2025-10-31T00:00:00",
  "location": "Global",
  "description": "The premier international MOBA championship.",
  "default_color": "#0ea5e9",
  "logo_path": "img/tournaments/worlds_logo.png",
  "banner_path": "img/tournaments/worlds_banner.jpg"
}'

# Major example
create_tournament '{
  "name": "Mid-Season Invitational",
  "abbreviation": "MSI",
  "type": "invitational",
  "format": "round_robin",
  "tier": "major",
  "start_date": "2025-05-05T00:00:00",
  "end_date": "2025-05-20T00:00:00",
  "location": "Europe",
  "description": "Top regional champions clash mid-season.",
  "default_color": "#a855f7",
  "logo_path": "img/tournaments/msi_logo.png",
  "banner_path": "img/tournaments/msi_banner.jpg"
}'

# League example
create_tournament '{
  "name": "Spring Split",
  "abbreviation": "Spring",
  "type": "league",
  "format": "bo3_series",
  "tier": "league",
  "start_date": "2025-02-01T00:00:00",
  "end_date": "2025-04-01T00:00:00",
  "location": "North America",
  "description": "Regional league spring season.",
  "default_color": "#3b82f6",
  "logo_path": "img/tournaments/spring_logo.png",
  "banner_path": "img/tournaments/spring_banner.jpg"
}'

# Minor example
create_tournament '{
  "name": "Rising Stars Cup",
  "abbreviation": "RSC",
  "type": "regional",
  "format": "single_elimination",
  "tier": "minor",
  "start_date": "2025-07-10T00:00:00",
  "end_date": "2025-07-15T00:00:00",
  "location": "Online",
  "description": "Minor tournament for up-and-coming teams.",
  "default_color": "#10b981",
  "logo_path": "img/tournaments/rsc_logo.png",
  "banner_path": "img/tournaments/rsc_banner.jpg"
}'

echo "Done."
