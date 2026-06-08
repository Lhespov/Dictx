#!/usr/bin/env python3
"""dictx - download a dictionary word list and extract words by prefix.

Downloads an English word list (cached locally after the first run) and prints
every word that starts with one of the prefixes you give it. Prefixes can be a
single letter, two letters, or any length ("a", "pre", "anti", ...).

Examples
--------
    # all words starting with "a"
    python3 dictx.py a

    # words starting with "pre" or "anti", case-insensitive (default)
    python3 dictx.py pre anti

    # just the count, no listing
    python3 dictx.py un --count

    # write matches to a file, only the first 50
    python3 dictx.py qu --limit 50 --output qu_words.txt

    # use your own word list instead of downloading
    python3 dictx.py xe --source /usr/share/dict/words
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

# A large, public-domain English word list (~370k lowercase words).
DEFAULT_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

# Where the downloaded list is cached so we only fetch it once.
DEFAULT_CACHE = Path(
    os.environ.get("DICTX_CACHE")
    or Path.home() / ".cache" / "dictx" / "words_alpha.txt"
)


def download_dictionary(url: str, cache: Path, force: bool = False) -> Path:
    """Return the path to a local copy of the word list, downloading if needed."""
    if cache.exists() and not force:
        return cache

    cache.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading dictionary from {url} ...", file=sys.stderr)
    tmp = cache.with_suffix(cache.suffix + ".tmp")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dictx/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as out:
            out.write(resp.read())
        tmp.replace(cache)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    print(f"Saved to {cache}", file=sys.stderr)
    return cache


def iter_words(path: Path):
    """Yield stripped, non-empty words from a word-list file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            word = line.strip()
            if word:
                yield word


def filter_by_prefix(words, prefixes, ignore_case: bool = True):
    """Yield words that start with any of the given prefixes."""
    if ignore_case:
        norm_prefixes = tuple(p.lower() for p in prefixes)
        for word in words:
            if word.lower().startswith(norm_prefixes):
                yield word
    else:
        norm_prefixes = tuple(prefixes)
        for word in words:
            if word.startswith(norm_prefixes):
                yield word


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dictx",
        description="Download a dictionary and extract words starting with a "
        "given letter / prefix.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "prefixes",
        nargs="+",
        metavar="PREFIX",
        help="one or more prefixes to match (e.g. 'a', 'pre', 'anti')",
    )
    parser.add_argument(
        "-c", "--count",
        action="store_true",
        help="print only the number of matches, not the words",
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=None,
        metavar="N",
        help="print at most N matches",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="write matches to FILE instead of stdout",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="match case-sensitively (default is case-insensitive)",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        metavar="FILE",
        help="use a local word-list file instead of downloading",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="URL to download the word list from (default: dwyl english-words)",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE,
        help=f"cache location for the downloaded list (default: {DEFAULT_CACHE})",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="re-download the word list even if it is already cached",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.source is not None:
            if not args.source.exists():
                print(f"error: source file not found: {args.source}", file=sys.stderr)
                return 2
            word_path = args.source
        else:
            word_path = download_dictionary(args.url, args.cache, force=args.refresh)
    except Exception as exc:  # network / IO errors
        print(f"error: could not obtain dictionary: {exc}", file=sys.stderr)
        return 1

    matches = filter_by_prefix(
        iter_words(word_path),
        args.prefixes,
        ignore_case=not args.case_sensitive,
    )

    # Count-only mode: consume the iterator and report the total.
    if args.count:
        total = sum(1 for _ in matches)
        print(total)
        return 0

    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    written = 0
    try:
        for word in matches:
            if args.limit is not None and written >= args.limit:
                break
            out.write(word + "\n")
            written += 1
    finally:
        if args.output:
            out.close()

    if args.output:
        print(f"Wrote {written} word(s) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
