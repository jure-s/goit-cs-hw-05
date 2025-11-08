from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .fetch import get_text, FetchError
from .mapreduce import mapreduce_count
from .visualize import visualize_top_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordcount-mr",
        description="Завантаження тексту за URL, підрахунок частот слів (MapReduce) та візуалізація TOP-N.",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL джерела тексту для аналізу.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Скільки найчастіших слів показати (за замовчуванням 20).",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=8,
        help="Кількість потоків для Map/Reduce (за замовчуванням 8).",
    )
    parser.add_argument(
        "--stop-words",
        type=Path,
        help="(Необов’язково) шлях до файлу зі стоп-словами, по одному слову в рядок.",
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=Path("data/output/top_words.png"),
        help="(Необов’язково) куди зберегти графік TOP-N слів (PNG).",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Не будувати графік, лише показати TOP-N у консолі.",
    )
    return parser


def _print_table(items: list[tuple[str, int]]) -> None:
    if not items:
        print("Немає даних (порожній текст або все відсіяно стоп-словами).")
        return
    w = max(len(word) for word, _ in items)
    print("\n📊 TOP-N слова:")
    for word, cnt in items:
        print(f"   {word.ljust(w)}  {cnt}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    url: str = args.url
    top_n: int = args.top
    threads: int = args.threads
    stop_words_path: Path | None = args.stop_words
    figure_path: Path = args.figure
    no_plot: bool = args.no_plot

    # Базові валідації
    if top_n <= 0:
        parser.error("--top має бути додатнім цілим числом.")
    if threads <= 0:
        parser.error("--threads має бути додатнім цілим числом.")
    if stop_words_path is not None and not stop_words_path.exists():
        parser.error(f"Файл стоп-слів не знайдено: {stop_words_path}")

    # Папка для графіка
    try:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        parser.error(
            f"Не вдалося створити директорію для фігури: {figure_path.parent}. Помилка: {e}"
        )

    # 1) Завантажуємо і чистимо текст
    try:
        text = get_text(url)
    except FetchError as e:
        print(f"Помилка завантаження: {e}", file=sys.stderr)
        return 2

    # 2) MapReduce-підрахунок
    top_items = mapreduce_count(
        text=text,
        threads=threads,
        stop_words_path=stop_words_path,
        top_n=top_n,
    )

    # 3) Вивід у консоль
    print("✅ Аналіз завершено.")
    print(f"   URL:        {url}")
    print(f"   THREADS:    {threads}")
    print(f"   STOP-WORDS: {stop_words_path if stop_words_path else '-'}")
    print(f"   TOP-N:      {top_n}")
    _print_table(top_items)

    # 4) Візуалізація (якщо не вимкнено)
    if not no_plot:
        out = visualize_top_words(top_items, figure_path, title=f"Top {top_n} words")
        print(f"\n🖼  Графік збережено: {out.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
