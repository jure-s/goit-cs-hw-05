from __future__ import annotations

import logging
import sys
from pathlib import Path

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s: %(message)s"
_DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _ensure_parent_dir(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Якщо не вдалося створити директорію під лог — просто ігноруємо,
        # logger все одно працюватиме з консольним хендлером.
        pass


def get_logger(
    name: str = "sorter_async",
    level: int = logging.INFO,
    log_file: Path | None = Path("data/output/sorter.log"),
) -> logging.Logger:
    """
    Повертає налаштований логер з консольним і (необов'язково) файловим хендлерами.
    Повторні виклики для того ж name не дублюють хендлери.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Перевіряємо, чи вже налаштовано (щоб не дублювати хендлери під час повторних імпортів)
    if getattr(logger, "_initialized", False):
        return logger

    formatter = logging.Formatter(_DEFAULT_FORMAT, datefmt=_DEFAULT_DATEFMT)

    # Console handler
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (якщо вказано шлях)
    if log_file is not None:
        _ensure_parent_dir(Path(log_file))
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            # Якщо файл недоступний — працюємо лише з консоллю
            logger.warning(
                "Не вдалося відкрити файл логу: %s. Продовжуємо без файлового логу.",
                log_file,
            )

    logger._initialized = True  # type: ignore[attr-defined]
    return logger
