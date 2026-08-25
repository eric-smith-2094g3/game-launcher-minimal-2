#!/usr/bin/env python3
"""Track time spent in games from launcher logs."""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# The launcher writes a line when a game starts and when it stops.
# Line format:
#   2024-01-15 21:04:12 START game_id
#   2024-01-15 22:47:03 STOP game_id

START_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) START (\S+)$')
STOP_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) STOP (\S+)$')

GAME_NAMES = {
    'sky_quest': 'Sky Quest',
    'dungeon_delver': 'Dungeon Delver',
    'hollow_knight': 'Hollow Knight',
    'stardew': 'Stardew Valley',
}

class Session:
    def __init__(self, game_id, start):
        self.game_id = game_id
        self.start = start
        self.end = None

    def duration(self):
        return self.end - self.start

def parse_log(path):
    sessions = []
    open_sessions = {}

    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = line.strip()
        if not line:
            continue

        start_match = START_RE.match(line)
        stop_match = STOP_RE.match(line)
        if start_match:
            ts = datetime.strptime(start_match.group(1), '%Y-%m-%d %H:%M:%S')
            game_id = start_match.group(2)
            sessions.append(Session(game_id, ts))
            open_sessions[len(sessions)-1] = sessions[-1]
        elif stop_match:
            ts = datetime.strptime(stop_match.group(1), '%Y-%m-%d %H:%M:%S')
            game_id = stop_match.group(2)
            # find the most recent open session for this game
            for idx in reversed(list(open_sessions)):
                if open_sessions[idx].game_id == game_id:
                    open_sessions[idx].end = ts
                    del open_sessions[idx]
                    break
            else:
                print(f"WARNING: STOP for {game_id} without matching START")

    # ignore sessions still running when the log ends
    return [s for s in sessions if s.end is not None]

def aggregate_by_game(sessions):
    totals = {}
    for s in sessions:
        totals[s.game_id] = totals.get(s.game_id, timedelta(0)) + s.duration()
    return totals

def format_duration(td):
    total_minutes = int(td.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours:
        return f"{hours}h"
    else:
        return f"{minutes}m"

def main():
    parser = argparse.ArgumentParser(
        description="Track time spent in games by parsing launcher logs.",
        epilog="example: %(prog)s -l launcher.log --json times.json"
    )
    parser.add_argument('-l', '--log', required=True, help='path to the launcher log file')
    parser.add_argument('--json', dest='json_out', help='write results as JSON to this file')
    parser.add_argument('--days', type=int, help='only count sessions within the last N days')
    args = parser.parse_args()

    log_path = Path(args.log)
    try:
        sessions = parse_log(log_path)
    except FileNotFoundError:
        print(f"error: log file not found: {log_path}")
        sys.exit(1)

    if args.days:
        cutoff = datetime.now() - timedelta(days=args.days)
        sessions = [s for s in sessions if s.start >= cutoff]

    totals = aggregate_by_game(sessions)

    # print report
    sorted_games = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    print("Game                Time")
    print("-------------------- -----")
    for game_id, td in sorted_games:
        name = GAME_NAMES.get(game_id, game_id)
        print(f"{name:<20} {format_duration(td)}")

    total = sum(totals.values(), timedelta(0))
    print(f"\nTotal: {format_duration(total)}")

    if args.json_out:
        out = {}
        for game_id, td in sorted_games:
            out[game_id] = int(td.total_seconds())
        out['total'] = int(total.total_seconds())
        try:
            Path(args.json_out).write_text(json.dumps(out, indent=2))
        except OSError as e:
            print(f"error: could not write {args.json_out}: {e}")
            sys.exit(1)

if __name__ == '__main__':
    import sys
    main()
