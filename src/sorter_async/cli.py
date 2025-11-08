import argparse
import sys
from pathlib import Path
import asyncio
import logging

from .sort_async import SortParams, sort_folder


def _apply_log_level(level_name: str) -> None:
    """
    Застосувати рівень логування до нашого логера та його хендлерів.
    """
    level = getattr(logging, level_name.upper(), logging.INFO)

    # Логер, який створюється у sort_async.get_logger(__name__)
    target_names = [
        "src.sorter_async.sort_async",  # точне ім'я
        "sorter_async",  # запасний варіант, якщо згодом використаємо інше ім'я
    ]
    for name in target_names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="async-sorter",
        description="Асинхронне сортування файлів по розширеннях у цільові підпапки.",
    )
    parser.add_argument(
        "--src",
        required=True,
        type=Path,
        help="Шлях до вихідної директорії з файлами (буде читатися рекурсивно).",
    )
    parser.add_argument(
        "--dst",
        required=True,
        type=Path,
        help="Шлях до цільової директорії, куди розкладати файли по розширеннях.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=100,
        help="Максимальна кількість одночасних копій/операцій (за замовчуванням 100).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Не виконувати копіювання, лише перевірити структуру/параметри та показати статистику.",
    )
    parser.add_argument(
        "--log-level",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        ],
        default="INFO",
        help="Рівень логування (за замовчуванням INFO).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    src: Path = args.src
    dst: Path = args.dst
    workers: int = args.workers
    dry_run: bool = args.dry_run
    log_level: str = args.log_level

    # Валідації
    if not src.exists() or not src.is_dir():
        parser.error(f"Директорія --src не існує або це не папка: {src}")

    # Створимо цільову папку, якщо її ще немає
    try:
        dst.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        parser.error(f"Не вдалося створити --dst: {dst}. Помилка: {e}")

    # Застосовуємо рівень логів ДО запуску сортування
    _apply_log_level(log_level)

    # Запускаємо асинхронне сортування
    params = SortParams(src=src, dst=dst, workers=workers, dry_run=dry_run)
    stats = asyncio.run(sort_folder(params))

    # Виводимо підсумок
    print("✅ Готово.")
    print(f"   SRC:     {src.resolve()}")
    print(f"   DST:     {dst.resolve()}")
    print(f"   WORKERS: {workers}")
    print(f"   DRY RUN: {dry_run}")
    print(f"   LOG LVL: {log_level.upper()}")
    if stats:
        print("\n📊 Статистика (папка → кількість файлів):")
        for folder, count in sorted(stats.items()):
            print(f"   {folder:12s} {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
