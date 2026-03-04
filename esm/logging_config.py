# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from contextvars import ContextVar

from esm.config import ESM_DIR


def _resolve_log_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level
    if not level:
        return logging.INFO
    normalized = str(level).upper()
    resolved = getattr(logging, normalized, logging.INFO)
    if isinstance(resolved, int):
        return resolved
    return logging.INFO


request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("-")
        return True


def configure_logging(
    level: str | int | None = None,
    log_file: Optional[Path | str] = None,
    force: bool = False,
) -> logging.Logger:
    logger = logging.getLogger("esm")
    if logger.handlers and not force:
        return logger
    if logger.handlers and force:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
    if force:
        logger.filters.clear()

    log_level = _resolve_log_level(level or os.getenv("ESM_LOG_LEVEL"))
    logger.setLevel(log_level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] [%(request_id)s] %(message)s"
    )

    request_filter = RequestIdFilter()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(request_filter)
    logger.addHandler(stream_handler)

    resolved_path: Optional[Path]
    if isinstance(log_file, str):
        resolved_path = Path(log_file) if log_file.strip() else None
    else:
        resolved_path = log_file
    if resolved_path is None:
        env_path = os.getenv("ESM_LOG_FILE")
        resolved_path = Path(env_path) if env_path else ESM_DIR / "logs" / "esm.log"

    try:
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            resolved_path,
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_filter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Unable to configure file logging at %s", resolved_path)

    logger.info("Logging configured level=%s", logging.getLevelName(log_level))
    return logger
