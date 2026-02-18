# TreasureMaze_v6_JoshDavila.py
# DB inspection + export + backup helpers.
import numpy as np
import time
import sqlite3
import csv
import shutil
from typing import List, Tuple, Optional, Set, Dict
from datetime import datetime

VISITED_MARK = 0.8
PIRATE_MARK = 0.5

# Movement actions
LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3

# Delta map for coordinates -> action
_DELTA_TO_ACTION = {
    (0, -1): LEFT,
    (-1, 0): UP,
    (0, 1): RIGHT,
    (1, 0): DOWN,
}

_ACTION_TO_DELTA = {v: k for k, v in _DELTA_TO_ACTION.items()}


class TreasureMaze:
    """
    Grid maze environment with small SQLite logging support and simple DB utilities.
    To enable logging, pass db_path to __init__, then call start_run(), use act(), and call end_run().
    """

    def __init__(self, maze: List[List[float]], pirate: Tuple[int, int] = (0, 0),
                 db_path: Optional[str] = None):
        self._maze = np.array(maze, dtype=float)
        if self._maze.ndim != 2:
            raise ValueError("Maze must be a 2D grid.")
        nrows, ncols = self._maze.shape
        self.target = (nrows - 1, ncols - 1)
        if self._maze[self.target] == 0.0:
            raise ValueError("Invalid maze: target cell cannot be blocked.")

        self.free_cells_all = [(r, c) for r in range(nrows) for c in range(ncols) if self._maze[r, c] == 1.0]
        # enforce pirate cannot start on target
        self.free_cells = [cell for cell in self.free_cells_all if cell != self.target]
        if pirate not in self.free_cells:
            raise ValueError("Invalid pirate location: must sit on a free cell (and not the target).")

        self.adjacency: Dict[Tuple[int, int], List[Tuple[Tuple[int, int], int]]] = {}
        self._build_adjacency()

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._cur = None
        self.current_run_id: Optional[int] = None
        self._step_counter = 0
        if self.db_path is not None:
            self._init_db(self.db_path)
        self.reset(pirate)

    # --------------------
    # Database helpers
    # --------------------
    def _init_db(self, db_path: str):
        """Initialize SQLite DB and create tables if they don't exist."""
        try:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._cur = self._conn.cursor()
            # Create runs table
            self._cur.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    end_time TEXT,
                    start_row INTEGER,
                    start_col INTEGER,
                    total_reward REAL
                )
            """)
            # Create moves table
            self._cur.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    move_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    step_number INTEGER,
                    row INTEGER,
                    col INTEGER,
                    action INTEGER,
                    reward REAL,
                    mode TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            self._conn.commit()
        except Exception as e:
            # If DB init fails, disable logging
            print(f"[DB] Initialization failed: {e}")
            self._conn = None
            self._cur = None
            self.db_path = None

    def start_run(self):
        """Start a new run record. Must be called to enable move logging."""
        if not self._cur:
            return
        row, col = self.state[0], self.state[1]
        start_time = datetime.utcnow().isoformat()
        self._cur.execute(
            "INSERT INTO runs (start_time, end_time, start_row, start_col, total_reward) VALUES (?, ?, ?, ?, ?)",
            (start_time, None, int(row), int(col), 0.0)
        )
        self._conn.commit()
        self.current_run_id = self._cur.lastrowid
        self._step_counter = 0

    def _log_move(self, action: Optional[int], reward: float, mode: str):
        """Internal helper to log a single move (only if a run is active)."""
        if not self._cur or self.current_run_id is None:
            return
        pirate_row, pirate_col, _ = self.state
        ts = datetime.utcnow().isoformat()
        self._step_counter += 1
        try:
            self._cur.execute(
                "INSERT INTO moves (run_id, step_number, row, col, action, reward, mode, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.current_run_id, self._step_counter, int(pirate_row), int(pirate_col),
                 None if action is None else int(action), float(reward), str(mode), ts)
            )
            self._conn.commit()
        except Exception as e:
            print(f"[DB] Move log failed: {e}")

    def end_run(self):
        """End the active run and update total_reward and end_time."""
        if not self._cur or self.current_run_id is None:
            return
        end_time = datetime.utcnow().isoformat()
        try:
            self._cur.execute(
                "UPDATE runs SET end_time = ?, total_reward = ? WHERE run_id = ?",
                (end_time, float(self.total_reward), int(self.current_run_id))
            )
            self._conn.commit()
        except Exception as e:
            print(f"[DB] End run update failed: {e}")
        finally:
            # reset current run
            self.current_run_id = None
            self._step_counter = 0

    def close_db(self):
        """Close DB connection gracefully (commit before closing)."""
        try:
            if self._conn:
                try:
                    self._conn.commit()
                except Exception:
                    pass
                self._conn.close()
        except Exception:
            pass
        finally:
            self._conn = None
            self._cur = None
            self.current_run_id = None

    def get_runs(self, limit: Optional[int] = None) -> List[Tuple]:
        """
        Return runs rows as a list of tuples for quick inspection.
        limit: optional maximum number of rows to return (most recent first).
        """
        if not self._cur:
            return []
        q = "SELECT run_id, start_time, end_time, start_row, start_col, total_reward FROM runs ORDER BY run_id DESC"
        if limit is not None:
            q += f" LIMIT {int(limit)}"
        try:
            self._cur.execute(q)
            rows = self._cur.fetchall()
            return rows
        except Exception:
            return []

    def export_run_csv(self, run_id: int, path: str) -> bool:
        """
        Export a run and its moves to a CSV file at `path`. Returns True on success.
        CSV columns: step_number,row,col,action,reward,mode,timestamp
        """
        if not self._cur:
            return False
        try:
            self._cur.execute(
                "SELECT step_number, row, col, action, reward, mode, timestamp FROM moves WHERE run_id = ? ORDER BY step_number",
                (int(run_id),)
            )
            rows = self._cur.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["step_number", "row", "col", "action", "reward", "mode", "timestamp"])
                for r in rows:
                    writer.writerow(r)
            return True
        except Exception as e:
            print(f"[DB] export_run_csv failed: {e}")
            return False

    def backup_db(self, backup_path: str) -> bool:
        """
        Make a filesystem copy (backup) of the current DB file. Returns True on success.
        If logging is not enabled or DB not present, returns False.
        """
        if not self.db_path:
            return False
        try:
            if self._conn:
                try:
                    self._conn.commit()
                except Exception:
                    pass
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"[DB] backup_db failed: {e}")
            return False

    # --------------------
    # Maze / logic code
    # --------------------
    def _build_adjacency(self):
        """Build adjacency mapping: cell -> list of (neighbor_coord, action)."""
        nrows, ncols = self._maze.shape
        for (r, c) in self.free_cells_all:
            neighbors: List[Tuple[Tuple[int, int], int]] = []
            # check four directions: LEFT, UP, RIGHT, DOWN
            for delta, action in _DELTA_TO_ACTION.items():
                dr, dc = delta
                nr, nc = r + dr, c + dc
                if 0 <= nr < nrows and 0 <= nc < ncols and self._maze[nr, nc] == 1.0:
                    neighbors.append(((nr, nc), action))
            self.adjacency[(r, c)] = neighbors

    def reset(self, pirate: Tuple[int, int]):
        """Reset environment and state."""
        self.pirate = pirate
        self.maze = np.copy(self._maze)
        row, col = pirate
        self.maze[row, col] = PIRATE_MARK
        self.state = (row, col, 'start')
        self.min_reward = -0.5 * self.maze.size
        self.total_reward = 0.0
        self.visited: Set[Tuple[int, int]] = set()
        self.visited.add((row, col))

    def update_state(self, action: int):
        """Update pirate state using adjacency for neighbor checks (faster)."""
        pirate_row, pirate_col, mode = self.state
        nrow, ncol, nmode = pirate_row, pirate_col, mode

        if self.maze[pirate_row, pirate_col] > 0.0:
            self.visited.add((pirate_row, pirate_col))

        valid_actions = self.valid_actions()

        if not valid_actions:
            nmode = 'blocked'
        elif action in valid_actions:
            nmode = 'valid'
            dr, dc = _ACTION_TO_DELTA[action]
            nrow, ncol = pirate_row + dr, pirate_col + dc
        else:
            nmode = 'invalid'

        # update visual markers
        try:
            self.maze[pirate_row, pirate_col] = VISITED_MARK if (pirate_row, pirate_col) in self.visited else 1.0
        except Exception:
            pass

        # sanity check: if move invalid wrt static maze, revert
        if not (0 <= nrow < self.maze.shape[0] and 0 <= ncol < self.maze.shape[1]) or self._maze[nrow, ncol] == 0.0:
            nrow, ncol = pirate_row, pirate_col
            nmode = 'blocked'

        self.maze[nrow, ncol] = PIRATE_MARK
        self.state = (nrow, ncol, nmode)

    def get_reward(self) -> float:
        pirate_row, pirate_col, mode = self.state
        nrows, ncols = self.maze.shape
        if (pirate_row, pirate_col) == self.target:
            return 1.0
        if mode == 'blocked':
            return self.min_reward - 1.0
        if (pirate_row, pirate_col) in self.visited:
            return -0.25
        if mode == 'invalid':
            return -0.75
        if mode == 'valid':
            return -0.04
        return -0.05

    def act(self, action: int):
        """
        Apply action, update state, compute reward, and return (envstate, reward, status).
        Logs moves to DB if a run is active.
        """
        self.update_state(action)
        reward = self.get_reward()
        self.total_reward += reward
        status = self.game_status()
        # Log move if DB run active
        try:
            self._log_move(action, reward, self.state[2])
        except Exception:
            pass
        envstate = self.observe()
        return envstate, reward, status

    def observe(self):
        canvas = self.draw_env()
        envstate = canvas.reshape((1, -1)).astype(float)
        return envstate

    def draw_env(self):
        canvas = np.copy(self.maze)
        nrows, ncols = canvas.shape
        for (r, c) in list(self.visited):
            if 0 <= r < nrows and 0 <= c < ncols and canvas[r, c] != PIRATE_MARK:
                canvas[r, c] = VISITED_MARK
        return canvas

    def game_status(self) -> str:
        if self.total_reward < self.min_reward:
            return 'lose'
        pirate_row, pirate_col, mode = self.state
        nrows, ncols = self.maze.shape
        if (pirate_row, pirate_col) == (nrows - 1, ncols - 1):
            return 'win'
        return 'not_over'

    def valid_actions(self, cell: Optional[Tuple[int, int]] = None) -> List[int]:
        """
        Return valid actions from the given cell or current state.
        Uses precomputed adjacency for O(1) neighbor lookup.
        """
        if cell is None:
            row, col, _ = self.state
            key = (row, col)
        else:
            row, col = cell
            key = (row, col)
        neighbors = self.adjacency.get(key, [])
        actions = [action for (_, action) in neighbors]

        return sorted(actions)

    def shortest_path(self, start: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        if start is None:
            start = (self.state[0], self.state[1])
        if start == self.target:
            return [start]
        from collections import deque
        queue = deque([start])
        parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        while queue:
            node = queue.popleft()
            for (nbr, _) in self.adjacency.get(node, []):
                if nbr not in parents:
                    parents[nbr] = node
                    if nbr == self.target:
                        path = [nbr]
                        cur = node
                        while cur is not None:
                            path.append(cur)
                            cur = parents[cur]
                        return list(reversed(path))
                    queue.append(nbr)
        return []

    def actions_from_path(self, path: List[Tuple[int, int]]) -> List[int]:
        if not path or len(path) < 2:
            return []
        actions: List[int] = []
        for (a, b) in zip(path, path[1:]):
            dr = b[0] - a[0]
            dc = b[1] - a[1]
            action = _DELTA_TO_ACTION.get((dr, dc))
            if action is None:
                raise ValueError(f"Non-adjacent steps in path: {a} -> {b}")
            actions.append(action)
        return actions

    def benchmark_valid_actions(self, runs: int = 1000) -> float:
        start = time.perf_counter()
        for _ in range(runs):
            _ = self.valid_actions()
        end = time.perf_counter()
        avg_sec = (end - start) / runs
        return avg_sec * 1e6  # microseconds per call

    def __del__(self):
        try:
            self.close_db()
        except Exception:
            pass


def _demo_run():
    maze = [
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 0.0, 1.0, 1.0],
    ]

    tm = TreasureMaze(maze, pirate=(0, 0), db_path="treasuremaze_demo.db")
    tm.start_run()

    path = tm.shortest_path()
    actions = tm.actions_from_path(path)

    status = "not_over"
    for a in actions:
        _, _, status = tm.act(a)
        if status != "not_over":
            break

    tm.end_run()

    runs = tm.get_runs(limit=1)
    if runs:
        run_id = runs[0][0]
        tm.export_run_csv(run_id, "treasuremaze_demo_moves.csv")

    tm.backup_db("treasuremaze_demo_backup.db")
    tm.close_db()
    return status


def _benchmark():
    maze = [[1.0] * 10 for _ in range(10)]
    tm = TreasureMaze(maze, pirate=(0, 0), db_path=None)
    return tm.benchmark_valid_actions(runs=5000)


import unittest


class TestTreasureMaze(unittest.TestCase):
    def test_target_not_blocked(self):
        maze = [[1.0, 1.0], [1.0, 1.0]]
        tm = TreasureMaze(maze, pirate=(0, 0))
        self.assertEqual(tm.target, (1, 1))

    def test_invalid_pirate_start(self):
        maze = [[1.0, 0.0], [1.0, 1.0]]
        with self.assertRaises(ValueError):
            TreasureMaze(maze, pirate=(0, 1))

    def test_shortest_path_reaches_target(self):
        maze = [
            [1.0, 1.0, 1.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
        ]
        tm = TreasureMaze(maze, pirate=(0, 0))
        path = tm.shortest_path()
        self.assertTrue(path)
        self.assertEqual(path[-1], tm.target)

    def test_act_changes_state_or_blocks(self):
        maze = [[1.0, 1.0], [1.0, 1.0]]
        tm = TreasureMaze(maze, pirate=(0, 0))
        env1 = tm.observe().copy()
        tm.act(RIGHT)
        env2 = tm.observe().copy()
        self.assertEqual(env1.shape, env2.shape)


if __name__ == "__main__":
    print("demo status:", _demo_run())
    print("benchmark (us/call):", _benchmark())
    unittest.main(argv=["ignored"], exit=False)
