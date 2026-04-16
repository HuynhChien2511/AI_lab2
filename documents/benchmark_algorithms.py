"""
Benchmark script to test all 4 search algorithms on square maps with increasing sizes (without obstacles).
Algorithms: BFS, DFS, A*, Best-First Search
Fixed seed: 1
"""

from lab2.vacuum import VacuumEnvironment, ENV_CLEAN, ENV_DIRTY, ENV_WALL
from lab2.myvacuumagent import MyVacuumAgent
import time
import csv
from datetime import datetime

# Configuration
DIRT_BIAS = 0.5
WALL_BIAS = 0.0
FIXED_SEED = 1
SEARCH_ALGORITHMS = ["BREADTH_FIRST_SEARCH", "DEPTH_FIRST_SEARCH", "A_STAR_SEARCH", "BEST_FIRST_SEARCH"]
MAP_SIZES = [5, 10, 15, 20, 25]

# Silent logger
def silent_log(msg):
    pass

def run_simulation(width, height, search_mode, seed):
    """
    Run a single simulation and collect results.
    Returns: metrics dict with all required data
    """
    # Create environment and agent
    env = VacuumEnvironment(width, height, DIRT_BIAS, WALL_BIAS, seed)
    agent = MyVacuumAgent(width, height, silent_log, search_mode=search_mode)
    env.add_thing(agent)
    
    # Run simulation
    start_time = time.time()
    step_count = 0
    max_steps = width * height * 10 + 100  # Safety limit
    
    while agent.alive and step_count < max_steps:
        env.step()
        step_count += 1
    
    elapsed_time = time.time() - start_time
    
    # Calculate optimality: for exploration task, optimality is approximate
    # A solution is considered optimal if the agent visited all reachable cells efficiently
    total_dirty_cells = sum(1 for x in range(width) for y in range(height) 
                            if env.world[x][y] == ENV_DIRTY)
    visited_clean = sum(1 for x in range(width) for y in range(height)
                        if env.world[x][y] == ENV_CLEAN and (x, y) in agent.visited_locations)
    
    # Estimate optimality (simplified)
    # Optimal = visited all cells with minimal redundancy
    efficiency = len(agent.visited_locations) / step_count if step_count > 0 else 0
    is_optimal = efficiency > 0.8  # heuristic threshold
    
    # Collect metrics
    return {
        'nodes_expanded': agent.search_nodes_expanded,
        'solution_length': step_count,
        'explored_locations': len(agent.visited_locations),
        'performance': agent.performance,
        'score': agent.score,
        'cleaned': agent.cleaned,
        'is_optimal': is_optimal,
        'time': elapsed_time
    }

def main():
    print("=" * 100)
    print(f"BENCHMARK: BFS vs A* Algorithm Comparison (No Obstacles)")
    print(f"Configuration: Seed={FIXED_SEED}, Dirt Bias={DIRT_BIAS}, Wall Bias={WALL_BIAS}")
    print("=" * 100)
    print()
    
    # Prepare results storage
    results = []
    
    # Test each map size
    for map_size in MAP_SIZES:
        print(f"\n📊 Testing {map_size}×{map_size} map ({map_size*map_size} cells)")
        print("-" * 100)
        
        size_results = {
            'map_size': map_size,
            'cells': map_size * map_size,
            'results': {}
        }
        
        # Test each algorithm
        for algo in SEARCH_ALGORITHMS:
            print(f"  Running {algo}...", end=" ", flush=True)
            
            try:
                metrics = run_simulation(map_size, map_size, algo, FIXED_SEED)
                size_results['results'][algo] = metrics
                
                print(f"✓ Done")
                print(f"    • Nodes expanded: {metrics['nodes_expanded']}")
                print(f"    • Solution length (steps): {metrics['solution_length']}")
                print(f"    • Explored locations: {metrics['explored_locations']}")
                print(f"    • Is optimal: {metrics['is_optimal']}")
                print(f"    • Performance score: {metrics['performance']:.0f}")
                print(f"    • Time: {metrics['time']:.2f}s")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                size_results['results'][algo] = None
        
        results.append(size_results)
    
    # Generate results table matching the required format
    print("\n\n" + "=" * 100)
    print("📋 RESULTS TABLE (Matching Lab Report Format)")
    print("=" * 100)
    print()
    
    table_header = f"{'Environment':<20} {'BFS #nodes':<15} {'BFS length':<15} {'BFS optimal?':<20} | {'A* #nodes':<15} {'A* length':<15} {'A* optimal?':<20}"
    print(table_header)
    print("-" * 105)
    
    for size_data in results:
        map_size = size_data['map_size']
        bfs_data = size_data['results']['BFS']
        astar_data = size_data['results']['ASTAR']
        
        if bfs_data and astar_data:
            bfs_nodes = bfs_data['nodes_expanded']
            bfs_length = bfs_data['solution_length']
            bfs_optimal = "Yes" if bfs_data['is_optimal'] else "No"
            bfs_score = bfs_data['performance']
            
            astar_nodes = astar_data['nodes_expanded']
            astar_length = astar_data['solution_length']
            astar_optimal = "Yes" if astar_data['is_optimal'] else "No"
            astar_score = astar_data['performance']
            
            row = f"{map_size}×{map_size:<15} {bfs_nodes:<15} {bfs_length:<15} {bfs_optimal} (↑{bfs_score:.0f})<8 | {astar_nodes:<15} {astar_length:<15} {astar_optimal} (↑{astar_score:.0f})"
            print(row)
    
    print("-" * 105)
    
    # Detailed comparison analysis
    print("\n\n" + "=" * 100)
    print("📈 EFFICIENCY ANALYSIS: BFS vs A* (Nodes Expanded)")
    print("=" * 100)
    
    for size_data in results:
        map_size = size_data['map_size']
        bfs_nodes = size_data['results']['BREADTH_FIRST_SEARCH']['nodes_expanded']
        astar_nodes = size_data['results']['A_STAR_SEARCH']['nodes_expanded']
        
        delta = ((astar_nodes - bfs_nodes) / bfs_nodes * 100) if bfs_nodes > 0 else 0
        winner = "Breadth-First Search" if bfs_nodes <= astar_nodes else "A* Search"
        
        print(f"\n{map_size}×{map_size} Map:")
        print(f"  Breadth-First Search:  {bfs_nodes} nodes")
        print(f"  A* Search:   {astar_nodes} nodes ({delta:+.1f}%)")
        print(f"  Winner: {winner} {'🏆' if delta <= 0 else ''}")
    
    # Save results to CSV and update markdown report
    csv_filename = save_to_csv(results)
    update_markdown_report(results, csv_filename)
    
    print(f"\n✅ Results saved to: {csv_filename}")
    print(f"📄 Report updated: LAB_REPORT.md")
    
    print("\n" + "=" * 100)
    print("✓ Benchmark completed!")
    print("=" * 100)

def save_to_csv(results, filename=None):
    """Save results to CSV file for further analysis."""
    if filename is None:
        filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Map Size', 'Total Cells', 'Algorithm', 
                'Nodes Expanded', 'Solution Length', 'Explored Locations', 
                'Is Optimal', 'Performance Score', 'Time (s)'
            ])
            
            # Write data
            for size_data in results:
                map_size = size_data['map_size']
                cells = size_data['cells']
                
                for algo in SEARCH_ALGORITHMS:
                    if size_data['results'][algo]:
                        m = size_data['results'][algo]
                        writer.writerow([
                            map_size, cells, algo,
                            m['nodes_expanded'], m['solution_length'], m['explored_locations'],
                            'Yes' if m['is_optimal'] else 'No', f"{m['performance']:.0f}", f"{m['time']:.2f}"
                        ])
    except Exception as e:
        print(f"Warning: Could not save CSV - {e}")
        return None
    
    return filename

def update_markdown_report(results, csv_filename):
    """Update LAB_REPORT.md with results table."""
    try:
        # Read existing report
        with open('LAB_REPORT.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Build results table
        table_lines = []
        table_lines.append("| Environment size (without obstacles) | BFS #nodes explored | BFS Solution length | BFS Is it optimal? Score? | A* #nodes explored | A* Solution length | A* Is it optimal? Score? |")
        table_lines.append("|---|---|---|---|---|---|---|")
        
        for size_data in results:
            map_size = size_data['map_size']
            bfs_data = size_data['results']['BFS']
            astar_data = size_data['results']['ASTAR']
            
            if bfs_data and astar_data:
                bfs_nodes = bfs_data['nodes_expanded']
                bfs_length = bfs_data['solution_length']
                bfs_optimal = "Yes" if bfs_data['is_optimal'] else "No"
                bfs_score = bfs_data['performance']
                
                astar_nodes = astar_data['nodes_expanded']
                astar_length = astar_data['solution_length']
                astar_optimal = "Yes" if astar_data['is_optimal'] else "No"
                astar_score = astar_data['performance']
                
                row = f"| {map_size}×{map_size} | {bfs_nodes} | {bfs_length} | {bfs_optimal} ({bfs_score:.0f}) | {astar_nodes} | {astar_length} | {astar_optimal} ({astar_score:.0f}) |"
                table_lines.append(row)
        
        # Replace the results table in markdown
        results_table = "\n".join(table_lines)
        
        # Find and replace the empty table
        start_marker = "### Results Table:\n\n"
        end_marker = "\n\n---"
        
        if start_marker in content:
            start_idx = content.find(start_marker) + len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                end_idx = content.find("\n\n##", start_idx)
            
            new_content = content[:start_idx] + results_table + content[end_idx:]
            
            # Write updated report
            with open('LAB_REPORT.md', 'w', encoding='utf-8') as f:
                f.write(new_content)
    except Exception as e:
        print(f"Warning: Could not update markdown report - {e}")

if __name__ == "__main__":
    main()
