from __future__ import annotations

import re
import time
from html import unescape
from typing import Final

import requests
from requests.exceptions import RequestException
from http.client import IncompleteRead


_UA: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_TAG_RE = re.compile(r"(?s)<[^>]+>")
_SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)\b.*?>.*?</\1>")
_WS_RE = re.compile(r"\s+")


class FetchError(RuntimeError):
    """Невдача під час отримання або попередньої обробки тексту."""


def _strip_html(html: str) -> str:
    # Прибираємо script/style, потім усі теги, розшифровуємо HTML-сутності та нормалізуємо пробіли.
    no_scripts = _SCRIPT_STYLE_RE.sub(" ", html)
    no_tags = _TAG_RE.sub(" ", no_scripts)
    text = unescape(no_tags)
    return _WS_RE.sub(" ", text).strip()


def get_text(url: str, timeout: float = 30.0, retries: int = 3, backoff: float = 0.7) -> str:
    """
    Завантажує HTML/текст із URL і повертає очищений plain-text.
    Має прості ретраї на випадок тимчасових мережевих збоїв.
    Підіймає FetchError у разі проблем.
    """
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout)
            resp.raise_for_status()
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "text" not in ctype and "json" not in ctype and "xml" not in ctype:
                raise FetchError(f"Непідтримуваний Content-Type: {ctype or '—'} для {url}")

            # .text інколи може впасти на розірваному потоці — страхуємось через повтор
            raw = resp.text
            cleaned = _strip_html(raw)
            if not cleaned:
                raise FetchError(f"Порожній або нечитабельний контент за адресою {url}")
            return cleaned

        except (RequestException, IncompleteRead) as e:
            last_exc = e
            if attempt == retries:
                break
            # експоненційна пауза перед наступною спробою
            time.sleep(backoff * attempt)

    raise FetchError(f"Помилка мережі для {url}: {last_exc}")
