#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2021 Joshua Bronson. All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Clone of `<http://play2048.co>`__.

See `<https://en.wikipedia.org/wiki/2048_(video_game)>`__.
"""

from copy import deepcopy
import curses
import random


N = 4  # NxN board
GOAL = 2048
# `Board.move()` below is generic and works with any of these directions,
# which are just lists of rows or cols of (r, c) positions in the right order:
UP = [[(r, c) for r in range(N)] for c in range(N)]
LEFT = [[(r, c) for c in range(N)] for r in range(N)]
DOWN = [i[::-1] for i in UP]
RIGHT = [i[::-1] for i in LEFT]
DIRS = (UP, LEFT, DOWN, RIGHT)
# Flattened list of positions (for checking empty cells below):
FLATPOS = [(r, c) for r in range(N) for c in range(N)]
MISS = (-1, -1)  # Sentinel for no such position


def randtile(choices=(2, 4), counts=(9, 1)):
    return random.sample(choices, 1, counts=counts)[0]


class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self._cells = [[None]*N for r in range(N)]
        self._add_tile_if_room()
        self._add_tile_if_room()
        self.won = False
        self.lost = False

    def _add_tile_if_room(self):
        empty = [(r, c) for (r, c) in FLATPOS if not self._cells[r][c]]
        if not empty:
            return
        r, c = random.choice(empty)
        tile = randtile()
        self._cells[r][c] = tile

    def move(self, dir, _just_checking=False) -> bool:
        moved = False
        b = deepcopy(self._cells) if _just_checking else self._cells
        for posns in dir:  # for each row (or col) of (r,c) positions in this direction
            for i, (r, c) in enumerate(posns):
                rest = posns[i+1:]
                if not b[r][c]:  # empty -> move next tile (if any) here
                    nr, nc = next(((nr, nc) for (nr, nc) in rest if b[nr][nc]), MISS)
                    if (nr, nc) != MISS:
                        b[r][c] = b[nr][nc]
                        b[nr][nc] = None
                        moved |= True
                if not b[r][c]:  # still empty -> no subsequent tiles
                    break
                # merge with next tile if match
                nr, nc = next(((nr, nc) for (nr, nc) in rest if b[nr][nc]), MISS)
                if (nr, nc) == MISS:
                    break
                if b[r][c] == b[nr][nc]:
                    b[nr][nc] = None
                    b[r][c] *= 2
                    moved |= True
                    self.won |= not _just_checking and b[r][c] == GOAL
        if not _just_checking:
            self.lost = not self.won and self._cant_move()
            if moved and not self.gameover:
                self._add_tile_if_room()
        return moved

    def _cant_move(self) -> bool:
        return not any(self.move(i, _just_checking=True) for i in DIRS)

    @property
    def gameover(self) -> bool:
        return self.won or self.lost

    def __repr__(self):
        s = "\n"
        for r in range(N):
            for c in range(N):
                s += f"{self._cells[r][c] or '•':^5}"
            s += "\n"
        return s


@curses.wrapper
def main(stdscr):
    b = Board()

    def redraw():
        stdscr.clear()
        stdscr.addstr(0, 0, str(b))
        stdscr.addstr(N + 2, 0, f"You {'won' if b.won else 'lost'}!" if b.gameover else "Use the arrow keys or H, J, K, L to move.")
        stdscr.addstr(N + 3, 0, "N for new game, Q to quit.")
        stdscr.refresh()

    redraw()

    def getkey():
        try:
            return stdscr.getkey().lower()
        except KeyboardInterrupt:
            return "q"

    while (key := getkey()) != "q":
        if key == "n":
            b.reset()
            redraw()
            continue
        if b.gameover:
            continue
        moved = False
        if key in ("h", "key_left"):
            moved = b.move(LEFT)
        elif key in ("l", "key_right"):
            moved = b.move(RIGHT)
        elif key in ("j", "key_down"):
            moved = b.move(DOWN)
        elif key in ("k", "key_up"):
            moved = b.move(UP)
        if moved or b.gameover:
            redraw()
