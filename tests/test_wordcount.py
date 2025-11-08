from pathlib import Path
import tempfile

from src.wordcount_mapreduce.mapreduce import mapreduce_count
from src.wordcount_mapreduce.visualize import visualize_top_words


def test_mapreduce_top_and_stopwords(tmp_path: Path):
    text = "Dog cat dog, bird! DOG; cat?\n" "mouse bird bird. the THE a an\n"
    # без стоп-слів
    top = dict(mapreduce_count(text, threads=4, top_n=3))
    assert top == {"dog": 3, "bird": 3, "cat": 2}

    # зі стоп-словами (приберемо артиклі "the", "a", "an" і слово mouse)
    stop = tmp_path / "stop.txt"
    stop.write_text("the\na\nan\nmouse\n", encoding="utf-8")
    top2 = dict(mapreduce_count(text, threads=4, top_n=4, stop_words_path=stop))
    # mouse відфільтрований, артиклі не потрапляють у TOP
    assert top2 == {"dog": 3, "bird": 3, "cat": 2}


def test_visualize_creates_png(tmp_path: Path):
    out = tmp_path / "chart.png"
    fig = visualize_top_words([("alpha", 5), ("beta", 3), ("gamma", 1)], out)
    assert fig.exists()
    assert fig.suffix.lower() == ".png"
