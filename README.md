# Dictx

A tiny command-line tool that **downloads an English dictionary word list and
extracts every word starting with a given letter (or prefix)**.

The prefix can be one letter, two letters, or any length — `a`, `qu`, `pre`,
`anti`, and so on. The word list is downloaded once and cached locally, so
later runs are instant.

No third-party dependencies. Use it two ways:

- **Web UI** — open `index.html` in a browser (or serve the folder) for a
  point-and-click interface.
- **CLI** — `dictx.py`, Python 3 standard library only.

## Web UI

**Live site:** https://lhespov.github.io/Dictx/ (published from this repo via
GitHub Actions — see `.github/workflows/pages.yml`). The page is
mobile-optimized: large touch targets, no zoom-on-focus, and a responsive
layout.

Or run it locally — just open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Type a prefix (or several, space/comma separated), hit **Extract words**, and
the matches appear instantly. You can:

- **Sort** results **alphabetically (A–Z)** or by **most common first** (usage
  frequency, from the top-30k word-frequency list).
- Set a result limit, toggle case-sensitivity, and copy or download the matches.

The dictionary is fetched once and cached for the session. It's a single static
file — host it anywhere (e.g. GitHub Pages) with no backend.

## CLI usage

```bash
# all words starting with "a"
python3 dictx.py a

# words starting with "pre" OR "anti" (case-insensitive by default)
python3 dictx.py pre anti

# just the count, no listing
python3 dictx.py un --count

# write the first 50 matches to a file
python3 dictx.py qu --limit 50 --output qu_words.txt

# use your own word list instead of downloading
python3 dictx.py xe --source /usr/share/dict/words
```

## Options

| Option | Description |
| --- | --- |
| `PREFIX...` | One or more prefixes to match (required). |
| `-c`, `--count` | Print only the number of matches. |
| `-n N`, `--limit N` | Print at most `N` matches. |
| `-o FILE`, `--output FILE` | Write matches to `FILE` instead of stdout. |
| `--case-sensitive` | Match case-sensitively (default is case-insensitive). |
| `--source FILE` | Use a local word-list file instead of downloading. |
| `--url URL` | Word-list URL to download (default: dwyl `english-words`). |
| `--cache PATH` | Where to cache the downloaded list. |
| `--refresh` | Re-download even if a cached copy exists. |

## Dictionary source

By default the word list comes from the public-domain
[dwyl/english-words](https://github.com/dwyl/english-words) project
(`words_alpha.txt`, ~370k lowercase words). It is cached at
`~/.cache/dictx/words_alpha.txt` (override with `--cache` or the `DICTX_CACHE`
environment variable).
