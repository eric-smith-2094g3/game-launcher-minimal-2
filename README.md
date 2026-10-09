# game-playtime-tracker

Tracks how much time I spend in each game by parsing the logs from my launcher (Steam, Epic, GOG, whatever). The store counters are always off or just don't reflect reality, so I made this to get my own numbers.

## Install

No dependencies, just Python 3.8+. Clone the repo and you're done.

## Run

```
python game_launcher_minimal_2.py --log /path/to/launcher.log
```

Options:
- `--log`: path to the log file (default: `launcher.log` in current dir)
- `--since`: only count sessions after this date (YYYY-MM-DD)
- `--until`: only count sessions before this date
- `--game`: filter to one game name (case-insensitive partial match)
- `--out`: write a summary to this file instead of printing

## Output

Prints a table like:

```
Game                Sessions   Total time
------------------------------------------
Elden Ring          12         42.5 hours
Disco Elysium       7          18.3 hours
```

Hours are shown with one decimal. If you want more precision, use `--out json` (well, `--out` takes a filename; the format is JSON if the filename ends with `.json`).

## How it works

It reads the log line by line, looks for lines that match the launcher's format:

```
2024-03-02 21:14:23 - GameName - Session start
2024-03-02 22:50:01 - GameName - Session end
```

Each start/end pair is a session. Sessions without an end (still running) are ignored. If the log doesn't match this format, the script will print a warning and continue.

The script doesn't modify the log, doesn't call any network, doesn't do anything fancy. It's a simple tool for a simple job.

## TODO

- Handle timezone offsets in log timestamps (currently assumes local time).
- Add a `--format` flag for different output styles.

## License

MIT (see LICENSE file).

---

This is a personal tool, not a library. It works for me; if your launcher logs a different format, you'll need to tweak the regex in `parse_line`.

<!-- last-checked: 2026-10-09 -->
