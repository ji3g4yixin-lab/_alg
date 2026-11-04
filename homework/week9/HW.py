"""
綜合搜尋演算法示範集
1. 老鼠走迷宮 (DFS)
2. 狼羊甘藍菜過河問題 (BFS)
3. 八皇后問題 (DFS Backtracking)
4. NPC 尋路 (A* Search)
5. IC 繞線 - Lee's Maze Routing Algorithm (BFS Grid Expansion)
"""

from collections import deque
import heapq


# =====================================================================
# 1. 老鼠走迷宮問題 (DFS)
# =====================================================================
def solve_maze_dfs(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    path = []

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if grid[r][c] == 1 or (r, c) in visited:
            return False

        visited.add((r, c))
        path.append((r, c))

        if (r, c) == end:
            return True

        # 探索順序：下、右、上、左
        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if dfs(r + dr, c + dc):
                return True

        path.pop()  # 回溯
        return False

    found = dfs(start[0], start[1])
    return path if found else None


# =====================================================================
# 2. 狼羊甘藍菜過河問題 (BFS)
# =====================================================================
def solve_river_crossing_bfs():
    # 狀態元組: (farmer, wolf, goat, cabbage)，0 代表左岸，1 代表右岸
    start_state = (0, 0, 0, 0)
    target_state = (1, 1, 1, 1)

    def is_safe(state):
        f, w, g, c = state
        if w == g and f != w:  # 狼羊同岸且無農夫
            return False
        if g == c and f != g:  # 羊菜同岸且無農夫
            return False
        return True

    queue = deque([(start_state, [start_state])])
    visited = {start_state}

    while queue:
        curr, path = queue.popleft()
        if curr == target_state:
            return path

        f, w, g, c = curr
        next_f = 1 - f

        # 農夫可單獨過河，或攜帶一隻同岸的物件
        moves = [(next_f, w, g, c)]
        if w == f: moves.append((next_f, 1 - w, g, c))
        if g == f: moves.append((next_f, w, 1 - g, c))
        if c == f: moves.append((next_f, w, g, 1 - c))

        for nxt in moves:
            if is_safe(nxt) and nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))

    return None


# =====================================================================
# 3. 八皇后問題 (DFS Backtracking)
# =====================================================================
def solve_n_queens_dfs(n=8):
    solutions = []
    current_board = []  # current_board[row] = col
    cols = set()
    diag1 = set()  # row - col
    diag2 = set()  # row + col

    def backtrack(row):
        if row == n:
            solutions.append(list(current_board))
            return

        for col in range(n):
            d1 = row - col
            d2 = row + col
            if col in cols or d1 in diag1 or d2 in diag2:
                continue

            # 做選擇
            cols.add(col)
            diag1.add(d1)
            diag2.add(d2)
            current_board.append(col)

            backtrack(row + 1)

            # 撤銷選擇
            current_board.pop()
            cols.remove(col)
            diag1.remove(d1)
            diag2.remove(d2)

    backtrack(0)
    return solutions


# =====================================================================
# 4. NPC 搜尋玩家問題 (A* Search)
# =====================================================================
def solve_npc_path_astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # 優先佇列內容: (f_score, g_score, current_node)
    pq = []
    heapq.heappush(pq, (heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}

    while pq:
        f, g, current = heapq.heappop(pq)

        if current == goal:
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            return path[::-1]

        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                tentative_g = g + 1
                neighbor = (nr, nc)
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(pq, (f_score, tentative_g, neighbor))

    return None


# =====================================================================
# 5. IC 設計電路繞線問題 (Lee's Maze Routing Algorithm)
# =====================================================================
def solve_ic_lee_routing(grid, pin_source, pin_sink):
    """
    Lee 演算法：以波前擴展（Wavefront Expansion, BFS）確保找到最短繞線路徑。
    grid: 0=空通道, 1=已佔用導線/障礙物
    """
    rows, cols = len(grid), len(grid[0])
    cost_grid = [[-1] * cols for _ in range(rows)]

    # 標記障礙物
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                cost_grid[r][c] = -2  # 障礙物標記

    # Phase 1: 波前擴展 (Expansion)
    queue = deque([pin_source])
    cost_grid[pin_source[0]][pin_source[1]] = 0
    reached = False

    while queue:
        r, c = queue.popleft()
        if (r, c) == pin_sink:
            reached = True
            break

        curr_cost = cost_grid[r][c]
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                # 只有未造訪過的網格 (-1) 才可以擴展
                if cost_grid[nr][nc] == -1:
                    cost_grid[nr][nc] = curr_cost + 1
                    queue.append((nr, nc))

    if not reached:
        return None

    # Phase 2: 逆向回溯 (Retrace)
    path = [pin_sink]
    curr = pin_sink
    while curr != pin_source:
        r, c = curr
        target_cost = cost_grid[r][c] - 1
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if cost_grid[nr][nc] == target_cost:
                    curr = (nr, nc)
                    path.append(curr)
                    break

    return path[::-1]


# =====================================================================
# 執行驗證
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("1. 老鼠走迷宮 (DFS)")
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    path_maze = solve_maze_dfs(maze, (0, 0), (4, 4))
    print(f"路徑點清單: {path_maze}")

    print("\n" + "=" * 60)
    print("2. 狼羊甘藍菜過河問題 (BFS)")
    river_steps = solve_river_crossing_bfs()
    names = ["農夫", "狼", "羊", "菜"]
    for i, step in enumerate(river_steps):
        left = [names[j] for j in range(4) if step[j] == 0]
        right = [names[j] for j in range(4) if step[j] == 1]
        print(f"步驟 {i}: 左岸 {left} | 右岸 {right}")

    print("\n" + "=" * 60)
    print("3. 八皇后問題 (DFS Backtracking)")
    n_queens_solutions = solve_n_queens_dfs(8)
    print(f"8 皇后總解法數量: {len(n_queens_solutions)}")
    print(f"第一組解的列位置: {n_queens_solutions[0]}")

    print("\n" + "=" * 60)
    print("4. NPC 搜尋玩家問題 (A*)")
    game_map = [
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]
    ]
    npc_start, player_pos = (0, 0), (4, 0)
    npc_path = solve_npc_path_astar(game_map, npc_start, player_pos)
    print(f"A* 最短導航路徑: {npc_path}")

    print("\n" + "=" * 60)
    print("5. IC 電路繞線 - Lee's Algorithm (BFS Maze Routing)")
    ic_grid = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ]
    source_pin, sink_pin = (0, 0), (2, 4)
    route = solve_ic_lee_routing(ic_grid, source_pin, sink_pin)
    print(f"接腳繞線路徑: {route}")