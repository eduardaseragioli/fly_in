*This project has been created as part of the 42 curriculum by eseragio*

## Description

Fly-in is a drone routing simulation project built as part of the 42 curriculum. The goal is to move a fleet of drones from a start zone to an end zone through an airspace graph, respecting zone capacity constraints, connection limits, and zone type rules — in the fewest number of turns possible.

### How it works

The airspace is represented as a weighted graph where each node is a zone and each edge is a connection between zones. Zones have types that affect movement:

- **Normal** — standard zone, costs 1 turn to enter
- **Restricted** — costs 2 turns to enter and occupies the connection during transit
- **Priority** — costs 1 turn but is preferred by the pathfinding algorithm
- **Blocked** — impassable, drones cannot enter

### Algorithms

**Dijkstra** is used to find the shortest path through the graph, respecting zone costs and preferring priority zones when paths have equal cost.

**Cooperative Pathfinding with Reservation Table** extends Dijkstra into space-time: each drone plans its route while avoiding zones and connections already reserved by previously planned drones. This allows multiple drones to navigate simultaneously without collisions, significantly reducing the
total number of turns required.

### Visualizer

After the simulation runs, a pygame window opens showing the airspace graph with animated drone movements. The visualizer supports three playback modes:

- **SPACE** — start or pause automatic playback
- **M** — manual mode, advance one turn per key press  
- **A** — automatic continuous playback

## Instructions

### Requirements

- Python 3.10 or higher
- pygame 2.0 or higher

Install dependencies:

```bash
pip install -r requirements.txt
```

### Installation

```bash
git clone https://github.com//fly_in.git
cd fly_in
make install
```

### Usage

```bash
make run FILE=maps/easy/01_linear_path.txt
```

Or directly:

```bash
python3 srcs/main.py maps/easy/01_linear_path.txt
```


### Map format

Maps are plain text files with the following structure:

```text
nb_drones: 

start_hub:    [color= max_drones=]
hub:    [color= zone= max_drones=]
end_hub:    [color= max_drones=]

connection: - [max_link_capacity=]
```

Zone types:
- `normal` — standard zone, costs 1 turn
- `restricted` — costs 2 turns, occupies connection during transit
- `priority` — costs 1 turn, preferred in pathfinding
- `blocked` — impassable

Example:

```text
nb_drones: 2

start_hub: start 0 0 [color=green max_drones=2]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Visualizer controls

### Visualizer controls

After the simulation completes, a pygame window opens automatically displaying
the airspace graph and the drone movements turn by turn.

| Key | Action |
|-----|--------|
| `SPACE` | Start or pause automatic playback |
| `M` | Switch to manual mode — advances one turn per key press |
| `A` | Switch to automatic continuous playback |

Zone colors displayed in the visualizer:

| Color | Zone type |
|-------|-----------|
| 🟢 Green | Normal zone |
| 🔴 Red | Blocked zone |
| 🔵 Dark blue | Restricted zone |
| 🟡 Yellow | Priority zone |

## Algorithmic choices

### Dijkstra

Dijkstra's algorithm was chosen as the base pathfinding algorithm because it guarantees the shortest path in a weighted graph and is straightforward to extend into space-time. 

Priority zones are preferred during pathfinding using a tiebreaker: when two paths have equal cost, the one passing through priority zones is chosen first.

### Cooperative Pathfinding with Reservation Table

With multiple drones navigating simultaneously, a single Dijkstra run per drone would cause collisions. The Reservation Table solves this by extending Dijkstra into space-time: each node in the search is a `(zone, turn)` pair instead of
just a zone.

Each drone plans its route sequentially. After a path is computed, all `(zone, turn)` pairs along that path are reserved. The next drone's search avoids any reserved `(zone, turn)` pairs, naturally finding a collision-free route even if it means waiting or taking a detour.

Drones may also wait in their current zone if all neighbors are reserved at the next turn, which is handled by adding a `(zone, turn + 1)` wait node to the search.

### Results

| Map | Target | Achieved |
|-----|--------|----------|
| Easy 01 — Linear path | ≤ 6 turns | 4 turns ✅ |
| Easy 02 — Simple fork | ≤ 8 turns | 6 turns ✅ |
| Easy 03 — Basic capacity | ≤ 8 turns | 6 turns ✅ |
| Medium 01 — Dead end trap | ≤ 12 turns | 8 turns ✅ |
| Medium 02 — Circular loop | ≤ 15 turns | 15 turns ✅ |
| Medium 03 — Priority puzzle | ≤ 12 turns | 8 turns ✅ |
| Hard 01 — Maze nightmare | ≤ 20 turns | 13 turns ✅ |
| Hard 02 — Capacity hell | ≤ 25 turns | 16 turns ✅ |
| Hard 03 — Ultimate challenge | ≤ 35 turns | 26 turns ✅ |
| Challenger — The impossible dream | ≤ 45 turns | 43 turns ✅ |

---

## Resources
- pygame documentation: https://www.pygame.org/docs/
- Python `heapq` documentation: https://docs.python.org/3library/heapq.html
- Python `abc` documentation: https://docs.python.org/3/library/abc.html

### References

- Dijkstra, E. W. (1959). *A note on two problems in connexion with graphs*. Numerische Mathematik, 1(1), 269–271.
- Silver, D. (2005). *Cooperative Pathfinding*. AAAI Workshop on Abstraction, Reformulation and Approximation.
- PyGame do Python – Como Criar Jogos no Python: https://www.hashtagtreinamentos.com/pygame-python


### AI usage

- **Debugging** — identifying and fixing logic errors in the simulator,
- **Visualizer** — help structuring the pygame loop, coordinate conversion, and drone animation
- **Docstrings and type hints** — Assistance in creating docstrings and adding type hints.