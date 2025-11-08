# goit-cs-hw-05 — Модуль «Асинхронна обробка»

Два незалежні завдання:

1) **Асинхронний сортер файлів** — рекурсивно обходить директорію-джерело та **асинхронно** розкладає файли по підпапках за розширеннями (`.jpg` → `jpg`, без розширення → `no_ext`), з обмеженням паралелізму та логуванням у консоль і файл.

2) **WordCount MapReduce + візуалізація** — завантажує текст за URL, виконує **паралельний** підрахунок частот слів (ThreadPoolExecutor, Map/Reduce), показує TOP-N у консолі та будує стовпчикову діаграму (PNG).

---

## Вимоги та інсталяція

- Python 3.10+
- Рекомендовано створити віртуальне середовище.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Unix:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Завдання 1: Асинхронний сортер

Точка входу: `src/sorter_async/cli.py`

```bash
# перегляд параметрів без копіювання (dry-run)
python -m src.sorter_async.cli --src data\sample_input --dst data\output --workers 50 --dry-run

# реальне копіювання
python -m src.sorter_async.cli --src data\sample_input --dst data\output --workers 50

# детальні логи (DEBUG)
python -m src.sorter_async.cli --src data\sample_input --dst data\output --workers 5 --log-level DEBUG
```

Особливості:
- неблокуюче копіювання через `asyncio.to_thread(shutil.copy2, ...)`;
- обмеження паралелізму `asyncio.Semaphore(workers)`;
- лог-файл: `data/output/sorter.log`.

---

## Завдання 2: WordCount MapReduce + Plot

Точка входу: `src/wordcount_mapreduce/cli.py`

```bash
# тільки консольний вивід TOP-N
python -m src.wordcount_mapreduce.cli --url https://example.com --top 10 --threads 4 --no-plot

# з побудовою графіка
python -m src.wordcount_mapreduce.cli --url https://example.com --top 5 --threads 4 --figure data\output\top_words.png
```

Параметри:
- `--top` — скільки частот показати (за замовчуванням 20).
- `--threads` — кількість потоків для map/reduce (за замовчуванням 8).
- `--stop-words PATH` — файл зі стоп-словами (по одному слову в рядок).
- `--no-plot` — не будувати графік.

Технічні нотатки:
- Спочатку **токенізуємо весь текст**, потім ділимо **список токенів** між потоками (щоб не ламати слова на межах шматків).
- Агрегація через `collections.Counter`.

---

## Тести

```bash
pytest
```

Очікувано: усі тести проходять.

---

## Структура проєкту

```
goit-cs-hw-05/
├─ src/
│  ├─ sorter_async/
│  │  ├─ cli.py
│  │  ├─ sort_async.py
│  │  └─ logger.py
│  └─ wordcount_mapreduce/
│     ├─ cli.py
│     ├─ fetch.py
│     ├─ mapreduce.py
│     └─ visualize.py
├─ tests/
│  ├─ test_sorter.py
│  └─ test_wordcount.py
├─ data/
│  ├─ sample_input/
│  └─ output/
├─ requirements.txt
├─ pytest.ini
├─ pyproject.toml
├─ .gitignore
└─ README.md
```

---
