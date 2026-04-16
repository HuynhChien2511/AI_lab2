# AI_Lab2: Vacuum Cleaner Agent with Search Algorithms

A comprehensive implementation of vacuum cleaner agents using multiple search algorithms (Breadth-First Search, Depth-First Search, A* Search, and Best-First Search).

## 📋 Project Overview

This project implements an intelligent vacuum cleaning agent in a gridworld environment with the ability to:
- Explore unknown areas efficiently
- Clean dirt when encountered
- Return home after exploration
- Compare performance across 4 different search algorithms

## 🎯 Features

### Search Algorithms Implemented
1. **Breadth-First Search (BFS)** - Uninformed, explores level-by-level
2. **Depth-First Search (DFS)** - Uninformed, explores deeply before backtracking
3. **A* Search** - Informed search using f(n) = g(n) + h(n), optimal with admissible heuristic
4. **Best-First Search** - Informed search using f(n) = h(n) only, faster but not optimal

### Heuristic Function
- **Manhattan Distance**: `h(n) = |x₁ - x₂| + |y₁ - y₂|`

### Environment Features
- Configurable grid size (5×5 to 25×25+)
- Tunable dirt and wall probabilities
- Fixed seed mode for reproducible benchmarking
- Real-time visualization via GUI
- Comprehensive performance metrics

## 📁 Project Structure

```
AI_Lab2/
├── lab2/
│   ├── __init__.py              # GUI implementation (Tkinter)
│   ├── myvacuumagent.py         # Main agent with all 4 algorithms
│   ├── vacuum.py                # Environment/world simulation
│   ├── randomvacuumagent.py     # Random baseline agent
│   └── reactivevacuumagent.py   # Reactive agent baseline
├── documents/
│   ├── benchmark_algorithms.py  # Automated benchmarking script
│   └── ALGORITHM_COMPARISON_REPORT.md
├── run_lab2.py                  # Main entry point
├── utils.py                     # Utility functions
└── README.md                    # This file
```

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AI_Lab2.git
cd AI_Lab2
```

2. Create virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. Run the GUI:
```bash
python run_lab2.py
```

### Running Benchmarks

Execute comprehensive benchmark across all algorithms:
```bash
cd documents
python benchmark_algorithms.py
```

Results will be saved to `benchmark_results_YYYYMMDD_HHMMSS.csv`

## 🎮 GUI Usage

1. **Select Parameters**:
   - Grid size (5×5 to 25×25)
   - Search algorithm (Breadth-First, Depth-First, A*, Best-First)
   - Dirt bias and wall bias
   - Random seed

2. **Run Simulation**:
   - Click "Start" to begin
   - Use continuous step or single step modes
   - Monitor performance metrics in real-time

3. **Observe Results**:
   - Visual grid with agent position
   - Log output showing decision process
   - Final metrics: nodes expanded, time, score

## 📊 Algorithm Comparison

### Performance on 25×25 Map (Benchmark Results)

| Algorithm | Nodes Expanded | Solution Length | Execution Time | Optimal |
|-----------|---|---|---|---|
| Breadth-First | 4534 | 1149 | 1.10s | ✅ Comparable |
| Depth-First | Variable | Variable | Varies | ❌ No |
| A* Search | 4066 | 1149 | 1.01s | ✅ Yes |
| Best-First | ~3500 | ~1160 | 0.95s | ❌ No |

### Key Findings

- **Small Maps (5×5)**: BFS most efficient, A* overhead too high
- **Medium Maps (10×20)**: BFS still competitive
- **Large Maps (25×25)**: A* becomes superior (10% fewer nodes)
- **Exploration Phase**: BFS optimal (heuristic misleads when goal unknown)
- **Return Home Phase**: A* and Best-First excel (clear goal)

## 🔧 Implementation Details

### Core Methods in MyVacuumAgent

```python
# Search algorithms (full names to avoid confusion)
breadth_first_search(return_home=False)
depth_first_search(return_home=False)
a_star_search(return_home=False)
best_first_search(return_home=False)

# Universal search interface
search_path(start_pos, goal_predicate, strategy, goal_pos=None)

# Manhattan distance heuristic
heuristic(pos, goal_pos)
```

### Key Configuration

- **Default search mode**: BREADTH_FIRST_SEARCH
- **Maximum iterations**: width × height × 10
- **Home position**: (1, 1)
- **Initial random actions**: 10 steps

## 📈 Benchmarking

The `benchmark_algorithms.py` script:
- Tests all 4 algorithms on 5 different map sizes
- Uses fixed seed for reproducibility
- Measures:
  - Nodes expanded
  - Solution length
  - Execution time
  - Performance score
- Exports results to CSV

## 🔍 Important Implementation Notes

### Bug Fixes Applied

1. **Re-planning Prevention**: Added `if not self.route:` check to avoid recalculating path every step
2. **Bump Handling**: Clear route when agent hits wall (`self.route = []`)
3. **Heuristic Correction**: Use BFS for exploration (no goal known), A*/Best-First only for return home

### Design Decisions

- **Unified search interface**: All algorithms use same `search_path()` method with strategy parameter
- **State tracking**: Maintains `visited_locations` to guide exploration
- **Priority queue**: Uses Python's `heapq` for A* and Best-First implementations
- **No obstacles in exploration**: Wall bias set to 0.0 by default for clean testing

## 📝 Code Quality

- Comprehensive docstrings for all methods
- Type hints in key functions
- Clear algorithm implementations
- Extensive comments explaining logic
- PEP 8 compatible

## 🎓 Learning Outcomes

This project demonstrates:
- Implementation of uninformed search (BFS, DFS)
- Implementation of informed search (A*, Best-First)
- Heuristic design and its impact
- Performance analysis and benchmarking
- Practical application in robotics/automation
- Software engineering best practices

## 📚 References

- Algorithm analysis based on AI: A Modern Approach (Russell & Norvig)
- Manhattan distance heuristic for grid navigation
- Tkinter for GUI implementation

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- More sophisticated heuristics
- Obstacle handling optimization
- Parallel benchmarking
- Advanced visualization
- More agent types

## 📄 License

This is an educational project for Lab 2.

## ✨ Version History

- **v1.0** (2026-04-16): Initial implementation with all 4 search algorithms
  - Breadth-First Search
  - Depth-First Search  
  - A* Search with Manhattan distance
  - Best-First Search
  - GUI with algorithm selection
  - Comprehensive benchmarking
  - Bug fixes for re-planning and heuristic

## 📧 Support

For questions or issues, refer to the comprehensive algorithm comparison report in `documents/ALGORITHM_COMPARISON_REPORT.md`

---

**Project Status**: ✅ Complete and Tested  
**Last Updated**: April 16, 2026
