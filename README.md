# CS 499 ePortfolio — Josh Davila

## Portfolio Overview

This repository contains my CS 499 capstone ePortfolio materials, including:
- An **informal code review** 
- The **original and enhanced artifact(s)**
- **Narratives** describing enhancements in:
  - Software Design & Engineering
  - Algorithms & Data Structures
  - Databases
- A **professional self-assessment** 

My primary artifact is **TreasureMaze.py**, a small grid-maze environment where an agent (“pirate”) navigates toward a treasure goal.

---

## Table of Contents
- [GitHub Pages (ePortfolio Site)](#github-pages-eportfolio-site)
- [Repository Structure](#repository-structure)
- [Informal Code Review (Text Version)](#informal-code-review-text-version)
- [Artifacts](#artifacts)
- [Enhancement Narratives](#enhancement-narratives)
  - [Enhancement 1: Software Design & Engineering](#enhancement-1-software-design--engineering)
  - [Enhancement 2: Algorithms & Data Structures](#enhancement-2-algorithms--data-structures)
  - [Enhancement 3: Databases](#enhancement-3-databases)
- [How to Run / Use TreasureMaze](#how-to-run--use-treasuremaze)
- [Planned Final Enhancements (Status)](#planned-final-enhancements-status)
- [Professional Self-Assessment (Draft)](#professional-self-assessment-draft)

---

## GitHub Pages (ePortfolio Site)

- **ePortfolio Home:** [LINK HERE]
- **Code Review Page/Section:** [LINK HERE]
- **Artifacts Page/Section:** [LINK HERE]
- **Narratives Page/Section:** [LINK HERE]

---

## Repository Structure

/ (repo root)
README.md
/artifacts
/original
TreasureMaze_v4_JoshDavila.py
/enhanced
TreasureMaze_v6_JoshDavila.py
/narratives
MilestoneTwo_EnhancementOne_SoftwareDesign.docx
MilestoneThree_EnhancementTwo_Algorithms.docx
MilestoneFour_EnhancementThree_Databases.docx
Professional_Self_Assessment.docx

---

## Informal Code Review (video skipped)

### Existing Functionality (Before Enhancements)
- The artifact is a **grid-based maze environment**.
- A “pirate” agent moves through free cells and attempts to reach the treasure at the bottom-right goal.
- The environment tracks state, visited cells, and rewards for movement outcomes.

### Code Analysis (Target Areas for Improvement)
Areas identified for improvement during planning included:
- **Modular design and maintainability**
- **Validation and safer handling of state changes**
- **Algorithm efficiency** (avoiding repeated neighbor checks)
- **Secure coding mindset** (defensive programming, safer DB operations later)

### Planned Enhancements (High-Level)
The planned improvements across categories included:
- Refactoring for clearer structure and better error handling
- Improving algorithm efficiency and adding measurable improvements
- Adding a database component with secure access patterns

---

## Artifacts

### Original Artifact
- `artifacts/original/TreasureMaze_v1_original.py`  *(original baseline)*

### Enhanced Artifact
- `artifacts/enhanced/TreasureMaze_v6_JoshDavila.py` *(enhanced across milestones)*

---

## Enhancement Narratives

### Enhancement 1: Software Design & Engineering
**What it is:**  
TreasureMaze is a compact environment class that models movement, state transitions, and rewards in a grid maze.

**Why I included it:**  
I chose this artifact because it is small enough to understand quickly, but it still demonstrates real software engineering skills—structure, correctness, validation, and maintainability.

**What I improved:**
- Fixed state update issues and standardized state handling
- Hardened validation (maze shape, blocked target, invalid start positions)
- Reduced fragile logic and made behavior more consistent

**What I learned**
Enhancing this artifact reinforced how small structural improvements can make code easier to extend and safer to modify later.

---

### Enhancement 2: Algorithms & Data Structures
**What I improved:**
- Added a **precomputed adjacency graph** for maze movement (neighbors for each free cell)
- Implemented **BFS shortest path** to the treasure
- Reduced repeated neighbor checking by using the precomputed graph

**Why this matters:**
This turns movement logic into a more efficient graph problem: neighbor lookup becomes fast and consistent, and shortest-path solving is a standard algorithmic approach that is easy to explain to employers.

**What I learned / reflection:**
This enhancement made the artifact feel more “computer science”—modeling the maze as a graph clarified the logic and enabled more efficient decision-making.

---

### Enhancement 3: Databases
For this milestone I added **optional SQLite logging** to capture experiment runs and moves:
- A `runs` table stores basic run metadata
- A `moves` table stores each step’s position, action, reward, and timestamp
- Logging is **optional** (only runs if a DB path is provided)
- SQL uses **parameterized queries**

**Why I included this:**
This demonstrates persistence, simple schema design, and secure DB interaction—useful for showing how results can be tracked and reviewed.

---

## How to Run / Use TreasureMaze

### Example without Database
```python
from TreasureMaze_v6_JoshDavila import TreasureMaze

maze = [
    [1.0, 1.0, 0.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0],
]

env = TreasureMaze(maze, pirate=(0, 0))
state = env.observe()

# Take an action (0=LEFT, 1=UP, 2=RIGHT, 3=DOWN)
envstate, reward, status = env.act(2)
print(reward, status)
```

### Example with SQLite Logging Enabled
```python
from TreasureMaze_v6_JoshDavila import TreasureMaze

maze = [
    [1.0, 1.0, 0.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0],
]

env = TreasureMaze(maze, pirate=(0, 0), db_path="treasuremaze_runs.db")
env.start_run()

# small demo loop
for action in [2, 3, 2, 3]:
    envstate, reward, status = env.act(action)
    if status != "not_over":
        break

env.end_run()

# Inspect recent runs
print(env.get_runs(limit=5))
```

### Exporting and Backing up
#### Export a specific run to CSV
```python
env.export_run_csv(run_id=1, path="run_1_moves.csv")
```
#### Backup the DB file
```python
env.backup_db("treasuremaze_runs_backup.db")
```
