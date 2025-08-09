uv run tailwindcss -i ./src/input.css -o ./src/output.css --minify &
uv run uvicorn dev:app --reload