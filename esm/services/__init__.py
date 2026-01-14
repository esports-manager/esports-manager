import aiofiles
import aiofiles.os
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
from typing import AsyncGenerator, Optional


async def create_streaming_response(image_path: Path) -> StreamingResponse:
    stat = await aiofiles.os.stat(image_path)
    etag = f"{image_path.name}-{stat.st_mtime}"

    async def filestreamer(file_path: Path) -> AsyncGenerator[bytes, None]:
        async with aiofiles.open(file_path, "rb") as file:
            while chunk := await file.read(8192):
                yield chunk

    return StreamingResponse(
        filestreamer(image_path),
        media_type=f"image/{image_path.suffix[1:]}",
        headers={
            "Cache-Control": "public, max-age=86400",
            "ETag": etag,
        },
    )


async def serve_image_async(
    image_path: Path, default_image: Optional[Path]
) -> Optional[StreamingResponse]:
    if not await aiofiles.os.path.exists(image_path):
        if default_image and await aiofiles.os.path.exists(default_image):
            return await create_streaming_response(default_image)
        return None

    if image_path.suffix.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        if default_image:
            return await create_streaming_response(default_image)
        return None

    return await create_streaming_response(image_path)


def serve_image(
    image_path: Path, default_image: Optional[Path]
) -> Optional[FileResponse]:
    if (
        not image_path.exists()
        or not image_path.is_file()
        or image_path.suffix not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    ):
        if not default_image:
            return None

        return FileResponse(
            default_image,
            media_type="image/webp",
            filename=default_image.name,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                "ETag": default_image.name,  # Add ETag for validation
            },
        )

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
