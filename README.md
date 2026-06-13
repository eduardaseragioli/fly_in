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

<!-- Explica os controlos do pygame:
- SPACE: iniciar/pausar
- M: modo manual
- A: modo automático
- R: reiniciar
-->

## Algorithmic choices

<!-- Explica as tuas escolhas:
- Porquê Dijkstra (simplicidade, optimalidade em grafos com pesos)
- Porquê Reservation Table (evitar colisões entre drones cooperativamente)
- Como funciona o space-time Dijkstra
- Resultados nos mapas (turnos obtidos vs targets)
-->

## Resources

### References

<!-- Lista as referências que usaste:
- Artigos, documentação, livros
-->

### AI usage

<!-- OBRIGATÓRIO pelo subject — explica honestamente:
- Que ferramentas de AI usaste (ex: Claude)
- Em que partes do projeto usaste (debugging, algoritmos, visualização, docstrings...)
- Como verificaste e adaptaste o código gerado
-->