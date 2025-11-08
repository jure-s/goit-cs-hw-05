import asyncio
from pathlib import Path
import shutil
import tempfile

from src.sorter_async.sort_async import SortParams, sort_folder


def _make_files(root: Path) -> dict[str, Path]:
    """Створює кілька файлів різних розширень і повертає мапу ім'я->шлях."""
    files = {
        "a.txt": root / "a.txt",
        "b.TXT": root / "nested" / "b.TXT",
        "c": root / "c",  # без розширення
        "d.docx": root / "nested" / "deep" / "d.docx",
    }
    for p in files.values():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("hello", encoding="utf-8")
    return files


def test_sorter_dry_run_and_real_copy():
    with (
        tempfile.TemporaryDirectory() as src_dir,
        tempfile.TemporaryDirectory() as dst_dir,
    ):
        src = Path(src_dir)
        dst = Path(dst_dir)

        # Підготуємо тестові файли
        _make_files(src)

        # 1) dry-run: підрахунок і створення цільових папок без копіювання
        stats = asyncio.run(
            sort_folder(SortParams(src=src, dst=dst, workers=5, dry_run=True))
        )
        assert stats == {"txt": 2, "no_ext": 1, "docx": 1}

        # Папки мали створитися, але файлів у них не має бути
        assert (dst / "txt").exists()
        assert (dst / "docx").exists()
        assert (dst / "no_ext").exists()
        assert list((dst / "txt").glob("*")) == []
        assert list((dst / "docx").glob("*")) == []
        assert list((dst / "no_ext").glob("*")) == []

        # 2) реальне копіювання
        stats2 = asyncio.run(
            sort_folder(SortParams(src=src, dst=dst, workers=5, dry_run=False))
        )
        assert stats2 == stats

        # Файли мають з'явитися в підпапках
        txt_files = sorted(f.name for f in (dst / "txt").glob("*"))
        docx_files = sorted(f.name for f in (dst / "docx").glob("*"))
        noext_files = sorted(f.name for f in (dst / "no_ext").glob("*"))

        assert txt_files == ["a.txt", "b.TXT"]
        assert docx_files == ["d.docx"]
        assert noext_files == ["c"]
