# CS 499 ePortfolio — Josh Davila

## Live ePortfolio

🔗 **GitHub Pages Site:**  
https://joshdavilasnhu.github.io/joshdavilaSNHU/

---

## Table of Contents
- [GitHub Pages (ePortfolio Site)](#github-pages-eportfolio-site)
- [Professional Self-Assessment](#professional-self-assessment)
- [Informal Code Review](##informal-code-review-(video-skipped))
- [Artifacts](#artifacts)
- [Enhancement Narratives](#enhancement-narratives)
  - [Enhancement 1: Software Design & Engineering](#enhancement-1-software-design--engineering)
  - [Enhancement 2: Algorithms & Data Structures](#enhancement-2-algorithms--data-structures)
  - [Enhancement 3: Databases](#enhancement-3-databases)
    
---

## Professional Self-Assessment

Throughout my coursework in the Computer Science program, I have developed a strong technical foundation across software engineering, algorithms, databases, and secure development practices. Completing the capstone project and building this ePortfolio allowed me to reflect on my growth while demonstrating my ability to enhance, analyze, and improve real code artifacts in a professional and structured manner.

During the program, I strengthened my ability to collaborate in structured environments by documenting design decisions, incorporating instructor feedback, and refining artifacts across multiple milestones. While many assignments were completed individually, the program emphasized clear communication with stakeholders through written documentation, structured code reviews, and professional justification of technical decisions. These experiences improved my ability to communicate complex technical concepts clearly and concisely to both technical and non-technical audiences.

From an algorithmic perspective, I gained practical experience implementing and analyzing data structures and efficiency trade-offs. In the TreasureMaze artifact, I enhanced the project by modeling the maze as a graph and implementing a breadth-first search (BFS) algorithm to compute the shortest path. This improvement demonstrates my understanding of graph traversal, time complexity considerations, and structured problem solving using established computer science principles.

In the area of software engineering and design, I improved the modular structure, input validation, and overall maintainability of the artifact. I reinforced best practices such as defensive programming, consistent state handling, and clear separation of responsibilities within the class design. These changes increased reliability and reduced logical fragility within the system.

For database integration, I implemented optional SQLite logging to persist run data and movement history. This enhancement demonstrates my understanding of relational database structure, schema design, and parameterized queries to reduce security risks such as SQL injection. It also shows my ability to extend a standalone application into a data-aware system capable of storing and exporting structured information.

Security awareness has become an integral part of my development mindset. Throughout the program, I learned to anticipate potential misuse, validate inputs, apply safer query handling techniques, and minimize unintended side effects within software systems. These principles were applied in the database enhancement and reinforced across improvements in input validation and error handling.

Collectively, the artifacts in this portfolio represent growth across three core areas of computer science: software design and engineering, algorithms and data structures, and databases. Each enhancement builds upon the previous version of the artifact, demonstrating my ability to iteratively evaluate, improve, and document computing solutions while considering trade-offs in design, efficiency, and maintainability.

This portfolio reflects not only my technical competency but also my ability to approach software development systematically, communicate professionally, and apply computing principles to produce structured, secure, and maintainable solutions.

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

### Original
[Original TreasureMaze](artifacts/original/TreasureMaze_v1_original.py)

### Enhanced
[Enhanced TreasureMaze (v6)](artifacts/enhanced/TreasureMaze_v6_JoshDavila.py)
---

## Enhancement Narratives

[Enhancement One – Software Design](narratives/3-2 Milestone Two_ Enhancement One_ Software Design and Engineering.docx)

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

[Enhancement Two – Algorithms](narratives/4-2 Milestone Three_ Enhancement Two_ Algorithms and Data Structure.docx)

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

[Enhancement Three – Databases](narratives/5-2 Milestone Four_ Enhancement Three_ Databases_JoshDavila.docx)

For this milestone I added **optional SQLite logging** to capture experiment runs and moves:
- A `runs` table stores basic run metadata
- A `moves` table stores each step’s position, action, reward, and timestamp
- Logging is **optional** (only runs if a DB path is provided)
- SQL uses **parameterized queries**

**Why I included this:**
This demonstrates persistence, simple schema design, and secure DB interaction—useful for showing how results can be tracked and reviewed.
