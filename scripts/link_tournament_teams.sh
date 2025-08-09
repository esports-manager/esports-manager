#!/usr/bin/env bash
# Link teams to a tournament via API
# Usage: ./scripts/link_tournament_teams.sh <tournament_id> <team_id> [<team_id> ...] [BASE_URL]
# Example: ./scripts/link_tournament_teams.sh 1 10 11 12 http://localhost:8000

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <tournament_id> <team_id> [<team_id> ...] [BASE_URL]" >&2
  exit 1
fi

TOURNAMENT_ID="$1"
shift

# Last arg may be a URL if it starts with http
BASE_URL_DEFAULT="http://localhost:8000"
if [[ "${@: -1}" =~ ^https?:// ]]; then
  BASE_URL="${@: -1}"
  set -- "${@:1:$(($#-1))}"
else
  BASE_URL="$BASE_URL_DEFAULT"
fi

API="$BASE_URL/api/moba/tournaments/$TOURNAMENT_ID/teams"

for TEAM_ID in "$@"; do
  echo "Linking team $TEAM_ID to tournament $TOURNAMENT_ID"
  curl -sS -X POST "$API" \
    -H 'Content-Type: application/json' \
    -d "{\"team_id\": $TEAM_ID}" >/dev/null
  echo " - done"
done

echo "All links processed."
