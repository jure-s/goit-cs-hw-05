from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.pyplot as plt


def visualize_top_words(
    top_items: Iterable[Tuple[str, int]],
    figure_path: Path | str,
    title: str = "Top words",
) -> Path:
    """
    Малює стовпчикову діаграму для списку (word, count) і зберігає у PNG.

    :param top_items: Iterable пар (слово, кількість), вже відсортований за спаданням.
    :param figure_path: Куди зберегти зображення (PNG).
    :param title: Заголовок графіка.
    :return: Шлях до збереженого файлу.
    """
    items = list(top_items)
    fig_path = Path(figure_path)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    if not items:
        # Створимо порожнє зображення з повідомленням
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "Немає даних для відображення", ha="center", va="center")
        plt.axis("off")
        plt.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close()
        return fig_path

    words = [w for w, _ in items]
    counts = [c for _, c in items]

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.title(title)
    plt.xlabel("Слова")
    plt.ylabel("Кількість")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    return fig_path
