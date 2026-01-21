#!/bin/bash

uv run scripts/init_db.py
uv run tailwindcss -i ./frontend/static/css/input.css -o ./frontend/static/css/tailwind.css --minify &
uv run uvicorn dev:app --reload