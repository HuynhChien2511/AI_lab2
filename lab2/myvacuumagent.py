from lab2.vacuum import *
from collections import deque
from random import random
import heapq

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3

def direction_to_string(cdr):
    cdr %= 4
    return  "NORTH" if cdr == AGENT_DIRECTION_NORTH else\
            "EAST"  if cdr == AGENT_DIRECTION_EAST else\
            "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else\
            "WEST" #if dir == AGENT_DIRECTION_WEST

"""
Internal state of a vacuum agent
"""
class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1

        # Metadata
        self.world_width = width
        self.world_height = height
        print(width, height)

    """
    Update perceived agent location
    """

    def update_position(self, bump):
        if self.last_action != ACTION_FORWARD:
            return
        if bump:
            return  # do NOT move into wall

        if self.direction == AGENT_DIRECTION_EAST:
            self.pos_x += 1
        elif self.direction == AGENT_DIRECTION_SOUTH:
            self.pos_y += 1
        elif self.direction == AGENT_DIRECTION_WEST:
            self.pos_x -= 1
        elif self.direction == AGENT_DIRECTION_NORTH:
            self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """

    def update_world(self, x, y, info):
        if 0 <= x < self.world_width and 0 <= y < self.world_height:
            self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """
    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print() # Newline
        print() # Delimiter post-print

"""
Vacuum agent
"""
class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log, search_mode=None):
        super().__init__(self.execute)

        self.initial_random_actions = 10
        self.iteration_counter = world_width * world_height * 10
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.search_mode = search_mode or "BREADTH_FIRST_SEARCH"
        self.search_mode = self.search_mode.strip().upper()
        # Support various naming conventions for A*
        if self.search_mode in {"A*", "ASTAR", "A_STAR"}:
            self.search_mode = "A_STAR_SEARCH"
        # Support various naming conventions for Best-First
        if self.search_mode in {"BESTFIRST", "BEST_FIRST", "BEST-FIRST"}:
            self.search_mode = "BEST_FIRST_SEARCH"
        if self.search_mode not in {"BREADTH_FIRST_SEARCH", "DEPTH_FIRST_SEARCH", "A_STAR_SEARCH", "BEST_FIRST_SEARCH"}:
            self.search_mode = "BREADTH_FIRST_SEARCH"

        #add new params for Lab2
        self.route = []  # acts like stack
        self.home_pos = (1, 1)
        self.steps = 0
        self.cleaned = 0
        self.score = -1000
        self.terminated = False
        self.task_complete = False
        self.alive = True
        self.visited_locations = set()
        self.visited_locations.add((1, 1))
        self.search_nodes_expanded = 0

    def update_score(self, action, shutdown=False):
        if self.terminated:
            return  # prevent ANY further scoring

        if shutdown:
            self.score += 1000
            self.terminated = True  # lock system
        elif action == ACTION_SUCK:
            self.score += 100
        else:
            self.score -= 1

    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:   # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            self.update_score(ACTION_TURN_LEFT)
            return ACTION_TURN_LEFT
        elif action < 0.3333333: # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            self.update_score(ACTION_TURN_RIGHT)
            return ACTION_TURN_RIGHT
        else:                    # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            self.update_score(ACTION_FORWARD)
            return ACTION_FORWARD

    def get_position_in_direction(self, x, y, direction):
        """Calculate position one step ahead in given direction"""
        if direction == AGENT_DIRECTION_EAST:
            return x + 1, y
        elif direction == AGENT_DIRECTION_SOUTH:
            return x, y + 1
        elif direction == AGENT_DIRECTION_WEST:
            return x - 1, y
        elif direction == AGENT_DIRECTION_NORTH:
            return x, y - 1
        return x, y

    def is_traversable(self, x, y):
        """Check if a position is within bounds and not a wall"""
        return 0 <= x < self.state.world_width and 0 <= y < self.state.world_height and self.state.world[x][y] != AGENT_STATE_WALL

    def heuristic(self, pos, goal_pos):
        """Manhattan distance heuristic for A* search"""
        return abs(pos[0] - goal_pos[0]) + abs(pos[1] - goal_pos[1])

    def find_path_to_frontier(self, start_pos):
        """Find a path to the nearest unvisited, non-wall cell using Breadth-First or Depth-First Search."""
        return self.search_path(
            start_pos,
            lambda cell: cell not in self.visited_locations and self.state.world[cell[0]][cell[1]] != AGENT_STATE_WALL,
            strategy=self.search_mode,
        )

    def search_path(self, start_pos, goal_predicate, strategy="BREADTH_FIRST_SEARCH", goal_pos=None):
        """Search for a path using Breadth-First, Depth-First, A*, or Best-First over the known traversable map."""
        if goal_predicate(start_pos):
            return [start_pos]

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        visited_search = {start_pos}

        if strategy == "BEST_FIRST_SEARCH":
            # Best-First Search with heuristic only (h(n) only, no g(n))
            if goal_pos is None:
                goal_pos = start_pos
            
            # Priority queue: (h_score, counter, pos, path)
            counter = 0
            frontier = [(self.heuristic(start_pos, goal_pos), counter, start_pos, [start_pos])]
            
            while frontier:
                _, _, (x, y), path = heapq.heappop(frontier)
                self.search_nodes_expanded += 1
                
                if goal_predicate((x, y)):
                    return path
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    next_pos = (nx, ny)
                    
                    if not self.is_traversable(nx, ny):
                        continue
                    
                    if next_pos in visited_search:
                        continue
                    
                    next_path = path + [next_pos]
                    h = self.heuristic(next_pos, goal_pos)
                    
                    visited_search.add(next_pos)
                    counter += 1
                    heapq.heappush(frontier, (h, counter, next_pos, next_path))
        
        elif strategy == "A_STAR_SEARCH":
            # A* search with priority queue
            if goal_pos is None:
                goal_pos = start_pos  # Fallback if no goal_pos provided
            
            # Priority queue: (f_score, counter, pos, path)
            counter = 0
            frontier = [(0, counter, start_pos, [start_pos])]
            g_score = {start_pos: 0}
            
            while frontier:
                _, _, (x, y), path = heapq.heappop(frontier)
                self.search_nodes_expanded += 1
                
                if goal_predicate((x, y)):
                    return path
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    next_pos = (nx, ny)
                    
                    if not self.is_traversable(nx, ny):
                        continue
                    
                    new_g = g_score[(x, y)] + 1
                    
                    if next_pos in visited_search and new_g >= g_score.get(next_pos, float('inf')):
                        continue
                    
                    next_path = path + [next_pos]
                    h = self.heuristic(next_pos, goal_pos)
                    f = new_g + h
                    
                    if next_pos not in visited_search or new_g < g_score.get(next_pos, float('inf')):
                        g_score[next_pos] = new_g
                        counter += 1
                        heapq.heappush(frontier, (f, counter, next_pos, next_path))
                        if next_pos not in visited_search:
                            visited_search.add(next_pos)
        
        elif strategy == "DEPTH_FIRST_SEARCH":
            frontier = [(start_pos, [start_pos])]
            while frontier:
                (x, y), path = frontier.pop()
                self.search_nodes_expanded += 1

                for dx, dy in reversed(directions):
                    nx, ny = x + dx, y + dy
                    next_pos = (nx, ny)

                    if not self.is_traversable(nx, ny):
                        continue

                    if next_pos in visited_search:
                        continue

                    next_path = path + [next_pos]
                    if goal_predicate(next_pos):
                        return next_path

                    visited_search.add(next_pos)
                    frontier.append((next_pos, next_path))
        else:  # BREADTH_FIRST_SEARCH (default)
            frontier = deque([(start_pos, [start_pos])])
            while frontier:
                (x, y), path = frontier.popleft()
                self.search_nodes_expanded += 1

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    next_pos = (nx, ny)

                    if not self.is_traversable(nx, ny):
                        continue

                    if next_pos in visited_search:
                        continue

                    next_path = path + [next_pos]
                    if goal_predicate(next_pos):
                        return next_path

                    visited_search.add(next_pos)
                    frontier.append((next_pos, next_path))

        return None

    def breadth_first_search(self, return_home=False):
        """Find path to unexplored area (or home if return_home=True) using Breadth-First Search"""
        current_pos = (self.state.pos_x, self.state.pos_y)
        
        if return_home:
            # Find path to home
            path = self.search_path(
                current_pos,
                lambda cell: cell == self.home_pos,
                strategy="BFS"
            )
        else:
            # Find path to nearest unknown or unexplored cell
            path = self.search_path(
                current_pos,
                lambda cell: cell not in self.visited_locations and self.state.world[cell[0]][cell[1]] == AGENT_STATE_UNKNOWN,
                strategy="BFS"
            )
        
        if path and len(path) > 1:
            self.route = path[1:]  # Remove current position from path

    def depth_first_search(self, return_home=False):
        """Find path to unexplored area (or home if return_home=True) using Depth-First Search"""
        current_pos = (self.state.pos_x, self.state.pos_y)
        
        if return_home:
            # Find path to home
            path = self.search_path(
                current_pos,
                lambda cell: cell == self.home_pos,
                strategy="DFS"
            )
        else:
            # Find path to nearest unknown or unexplored cell
            path = self.search_path(
                current_pos,
                lambda cell: cell not in self.visited_locations and self.state.world[cell[0]][cell[1]] == AGENT_STATE_UNKNOWN,
                strategy="DFS"
            )
        
        if path and len(path) > 1:
            self.route = path[1:]  # Remove current position from path

    def a_star_search(self, return_home=False):
        """Find path to unexplored area (or home if return_home=True) using A* Search"""
        current_pos = (self.state.pos_x, self.state.pos_y)
        
        if return_home:
            # Find path to home using A* with home as goal
            path = self.search_path(
                current_pos,
                lambda cell: cell == self.home_pos,
                strategy="A_STAR_SEARCH",
                goal_pos=self.home_pos
            )
        else:
            # For exploration, use BFS because we don't know where UNKNOWN cells are
            # A* with heuristic pointing to current_pos actually works against finding frontier!
            path = self.search_path(
                current_pos,
                lambda cell: cell not in self.visited_locations and self.state.world[cell[0]][cell[1]] == AGENT_STATE_UNKNOWN,
                strategy="BREADTH_FIRST_SEARCH"
            )
        
        if path and len(path) > 1:
            self.route = path[1:]  # Remove current position from path

    def best_first_search(self, return_home=False):
        """Find path to unexplored area (or home if return_home=True) using Best-First Search"""
        current_pos = (self.state.pos_x, self.state.pos_y)
        
        if return_home:
            # Find path to home using Best-First with home as goal
            path = self.search_path(
                current_pos,
                lambda cell: cell == self.home_pos,
                strategy="BEST_FIRST_SEARCH",
                goal_pos=self.home_pos
            )
        else:
            # For exploration, use BFS because we don't know where UNKNOWN cells are
            # Best-First with heuristic pointing to current_pos keeps agent looping near start!
            path = self.search_path(
                current_pos,
                lambda cell: cell not in self.visited_locations and self.state.world[cell[0]][cell[1]] == AGENT_STATE_UNKNOWN,
                strategy="BREADTH_FIRST_SEARCH"
            )
        
        if path and len(path) > 1:
            self.route = path[1:]  # Remove current position from path

    def move_to(self, target):
        cx, cy = self.state.pos_x, self.state.pos_y
        tx, ty = target
        dx = tx - cx
        dy = ty - cy
        # Determine target direction
        if abs(dx) > abs(dy):
            target_dir = AGENT_DIRECTION_EAST if dx > 0 else AGENT_DIRECTION_WEST
        else:
            target_dir = AGENT_DIRECTION_SOUTH if dy > 0 else AGENT_DIRECTION_NORTH
        # Compute turn
        turn = (target_dir - self.state.direction) % 4

        if turn == 1 or turn == 2:
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            self.update_score(ACTION_TURN_RIGHT)
            return ACTION_TURN_RIGHT

        elif turn == 3:
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            self.update_score(ACTION_TURN_LEFT)
            return ACTION_TURN_LEFT

        else:
            self.state.last_action = ACTION_FORWARD
            self.update_score(ACTION_FORWARD)
            self.route.pop(0)
            return ACTION_FORWARD

    def execute(self, percept):
        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK


        ########################
        # START MODIFYING HERE #
        ########################
        
        # Early termination check
        if self.terminated:
            return ACTION_NOP
        
        self.steps += 1
        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
                self.update_score(ACTION_NOP)
            return ACTION_NOP

        self.log("Position: ({}, {})\t\tDirection: {}".format(self.state.pos_x, self.state.pos_y,
                                                              direction_to_string(self.state.direction)))

        self.iteration_counter -= 1
        # Track position of agent
        self.state.update_position(bump)
        self.visited_locations.add((self.state.pos_x, self.state.pos_y))
        
        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(self.state.pos_x + offset[0], self.state.pos_y + offset[1], AGENT_STATE_WALL)
            
            # FIX #1: Clear route when bump - old path is invalid
            self.route = []

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)
        
        # Mark adjacent unknown cells for exploration
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = self.state.pos_x + dx, self.state.pos_y + dy
            if 0 <= nx < self.state.world_width and 0 <= ny < self.state.world_height:
                if self.state.world[nx][ny] == AGENT_STATE_UNKNOWN:
                    # Keep it unknown until we reach it
                    pass
        
        # Debug
        self.state.print_world_debug()

        # Save home position
        if home:
            self.home_pos = (self.state.pos_x, self.state.pos_y)

        # Decide action
        # ---- CLEAN ----
        if dirt:
            self.log("DIRT -> SUCK")
            self.state.last_action = ACTION_SUCK
            self.cleaned += 1
            self.update_score(ACTION_SUCK)
            return ACTION_SUCK

        # ---- PLAN ----
        if not self.task_complete:
            # FIX #1: Only plan if we don't have a route - avoid re-planning every step!
            if not self.route:
                # explore unknown first
                if self.search_mode == "BREADTH_FIRST_SEARCH":
                    self.breadth_first_search(return_home=False)
                    self.log(f"Following {self.search_mode} path to frontier")
                elif self.search_mode == "DEPTH_FIRST_SEARCH":
                    self.depth_first_search(return_home=False)
                    self.log(f"Following {self.search_mode} path to frontier")
                elif self.search_mode == "A_STAR_SEARCH":
                    self.a_star_search(return_home=False)
                    self.log(f"Following {self.search_mode} path to frontier (return_home=False)")
                else:  # BEST_FIRST_SEARCH
                    self.best_first_search(return_home=False)
                    self.log(f"Following {self.search_mode} path to frontier (return_home=False)")
            # if no unknown → mark task complete
            if not self.route:
                self.log("All reachable areas explored! Returning home...")
                self.task_complete = True

        if self.task_complete:
            if (self.state.pos_x, self.state.pos_y) == self.home_pos:
                self.log("FINISHED: cleaned entire map and returned home")
                self.log("Search nodes expanded: {}".format(self.search_nodes_expanded))
                self.log("Explored locations: {}".format(len(self.visited_locations)))
                self.log("Performance: {}".format(self.performance))
                self.state.print_world_debug()
                self.update_score(ACTION_NOP, shutdown=True)
                print("Score: ", self.score)
                self.alive = False
                self.terminated = True
                return ACTION_NOP

            # Not at home yet, plan path home
            # FIX #1: Only plan if we don't have a route
            if not self.route:
                if self.search_mode == "BREADTH_FIRST_SEARCH":
                    self.breadth_first_search(return_home=True)
                elif self.search_mode == "DEPTH_FIRST_SEARCH":
                    self.depth_first_search(return_home=True)
                elif self.search_mode == "A_STAR_SEARCH":
                    self.a_star_search(return_home=True)
                else:  # BEST_FIRST_SEARCH
                    self.best_first_search(return_home=True)

        # ---- EXECUTE PLAN ----
        if self.route:
            return self.move_to(self.route[0])
        
        # No route and not at goal - continue moving
        self.state.last_action = ACTION_FORWARD
        self.update_score(ACTION_FORWARD)
        return ACTION_FORWARD
