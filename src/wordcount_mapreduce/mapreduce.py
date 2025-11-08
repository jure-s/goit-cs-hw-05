from __future__ import annotations

import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, List

_WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁїЇіІєЄґҐ']+")


def _tokenize(text: str) -> list[str]:
    """Розбиває текст на слова (латиниця + кирилиця), повертає у нижньому регістрі."""
    return [w.lower() for w in _WORD_RE.findall(text)]


def _map_chunk_tokens(words: list[str], stop_words: set[str]) -> Counter[str]:
    """Map: підрахунок слів у одному шматку (список уже-токенізованих слів)."""
    if stop_words:
        words = [w for w in words if w not in stop_words]
    return Counter(words)


def _split_tokens(words: list[str], parts: int) -> list[list[str]]:
    """
    Ділить список слів на parts (≈ рівні за розміром) без ламання слів.
    Порожні шматки відкидаємо.
    """
    n = len(words)
    if n == 0 or parts <= 1:
        return [words] if words else []
    step = max(1, n // parts)
    chunks: list[list[str]] = [words[i : i + step] for i in range(0, n, step)]
    return [c for c in chunks if c]  # без порожніх


def mapreduce_count(
    text: str,
    threads: int = 8,
    stop_words_path: Path | None = None,
    top_n: int = 20,
) -> list[tuple[str, int]]:
    """
    Виконує MapReduce-підрахунок слів.
    Повертає TOP-N (word, count) у порядку спадання.
    """
    # 1) Токенізуємо один раз — надалі працюємо з цілими словами
    words_all = _tokenize(text)

    # 2) Завантажуємо стоп-слова
    stop_words: set[str] = set()
    if stop_words_path and stop_words_path.exists():
        with open(stop_words_path, encoding="utf-8") as f:
            stop_words = {w.strip().lower() for w in f if w.strip()}

    # 3) Розбиваємо токени на шматки для потоків
    chunks = _split_tokens(words_all, max(1, threads))
    total_counter: Counter[str] = Counter()

    # 4) Map у потоках + Reduce через Counter.update()
    if not chunks:
        return []

    with ThreadPoolExecutor(max_workers=min(len(chunks), threads)) as executor:
        futures = [
            executor.submit(_map_chunk_tokens, chunk, stop_words) for chunk in chunks
        ]
        for fut in as_completed(futures):
            total_counter.update(fut.result())

    # 5) Отримуємо TOP-N
    return total_counter.most_common(top_n)
