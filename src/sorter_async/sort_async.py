from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class SortParams:
    src: Path
    dst: Path
    workers: int = 100
    dry_run: bool = False


def _ext_folder(path: Path) -> str:
    """
    Обчислює назву цільової папки за розширенням файлу.
    '.JPG' -> 'jpg', '.tar.gz' -> 'gz' (беремо останнє), без розширення -> 'no_ext'.
    """
    if not path.suffix:
        return "no_ext"
    return path.suffix.lstrip(".").lower()


def _iter_files(src: Path) -> Iterable[Path]:
    """Рекурсивно повертає всі файли з дерева каталогу src."""
    yield from (p for p in src.rglob("*") if p.is_file())


async def _copy_one(
    src_file: Path, dst_root: Path, sem: asyncio.Semaphore, dry_run: bool
):
    """
    Копіює один файл у відповідну підпапку dst_root за розширенням.
    Повертає (src_file, dst_file) при успіху, або None при dry-run.
    """
    folder = _ext_folder(src_file)
    dst_dir = dst_root / folder
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_file = dst_dir / src_file.name

    async with sem:
        if dry_run:
            logger.debug("[dry-run] %s -> %s", src_file, dst_file)
            return None
        try:
            await asyncio.to_thread(shutil.copy2, src_file, dst_file)
            logger.debug("copied %s -> %s", src_file, dst_file)
            return (src_file, dst_file)
        except Exception as e:
            logger.error("copy failed %s -> %s: %s", src_file, dst_file, e)
            # Прокидуємо виняток далі, щоб підсумково порахувати помилки
            raise


async def sort_folder(params: SortParams) -> dict[str, int]:
    """
    Асинхронно сортує всі файли з params.src по підпапках у params.dst за розширеннями.
    Повертає статистику: {<ext_folder>: <count>}.
    """
    if not params.src.exists() or not params.src.is_dir():
        raise ValueError(f"--src не існує або це не директорія: {params.src}")
    params.dst.mkdir(parents=True, exist_ok=True)

    files = list(_iter_files(params.src))
    logger.info(
        "Start sorting: src=%s, dst=%s, workers=%d, dry_run=%s, files=%d",
        params.src.resolve(),
        params.dst.resolve(),
        params.workers,
        params.dry_run,
        len(files),
    )

    sem = asyncio.Semaphore(max(1, params.workers))

    tasks = [
        asyncio.create_task(_copy_one(f, params.dst, sem, params.dry_run))
        for f in files
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    stats: dict[str, int] = {}
    for f in files:
        folder = _ext_folder(f)
        stats[folder] = stats.get(folder, 0) + 1

    errors = [r for r in results if isinstance(r, Exception)]
    if errors and not params.dry_run:
        logger.warning("Completed with errors: %d file(s) failed", len(errors))
        # Залишаємо підняття помилки, щоб CI/тести могли це відловити
        raise RuntimeError(f"Кількість помилок під час копіювання: {len(errors)}")

    logger.info(
        "Done. Buckets: %s", ", ".join(f"{k}:{v}" for k, v in sorted(stats.items()))
    )
    return stats
