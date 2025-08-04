from fastapi.responses import FileResponse
from pathlib import Path
from esm.config import ESM_DIR


async def serve_image(image_path: Path):
    if (
        not image_path.exists()
        or not image_path.is_file()
        or image_path.suffix not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    ):
        # Return default image with cache headers
        return FileResponse(
            ESM_DIR / "res" / "img" / "players" / "default_player.webp",
            media_type="image/webp",
            filename="default_player.webp",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                "ETag": "default-player",  # Add ETag for validation
            },
        )

    # Generate a simple ETag based on filename and modification time
    stat = image_path.stat()
    etag = f"{image_path.name}-{stat.st_mtime}"

    return FileResponse(
        image_path,
        media_type="image/" + image_path.suffix[1:],
        filename=image_path.name,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 1 day
            "ETag": etag,  # Add ETag for validation
        },
    )


def get_country_code(nationality: str) -> str:
    import pycountry

    try:
        country = pycountry.countries.search_fuzzy(nationality)
        if country:
            return country[0].alpha_2.lower()
        else:
            return ""
    except LookupError:
        return ""
