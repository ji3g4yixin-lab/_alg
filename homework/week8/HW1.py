import math
import random
import time
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# 1. 基準數據與輔助函式
# -------------------------------------------------------------------------
def generate_cities(num_cities=20, seed=42):
    random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_cities)]

def euclidean_dist(c1, c2):
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])

def compute_total_distance(tour, cities):
    dist = 0.0
    n = len(tour)
    for i in range(n):
        dist += euclidean_dist(cities[tour[i]], cities[tour[(i + 1) % n]])
    return dist

# -------------------------------------------------------------------------
# 演算法 1: 貪婪演算法 (Nearest Neighbor)
# -------------------------------------------------------------------------
def solve_greedy(cities, start_index=0):
    n = len(cities)
    unvisited = set(range(n))
    current = start_index
    unvisited.remove(current)
    tour = [current]
    history = []

    while unvisited:
        next_city = min(unvisited, key=lambda city: euclidean_dist(cities[current], cities[city]))
        tour.append(next_city)
        unvisited.remove(next_city)
        current = next_city
        # 記錄部分路徑（含折返）的預估長度作為收斂動態
        history.append(compute_total_distance(tour, cities))

    return tour, history

# -------------------------------------------------------------------------
# 演算法 2: 改良法 (2-opt Improvement)
# -------------------------------------------------------------------------
def solve_2opt(tour, cities):
    n = len(tour)
    best_tour = list(tour)
    cur_dist = compute_total_distance(best_tour, cities)
    history = [cur_dist]
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                c_i_prev = cities[best_tour[i - 1]]
                c_i = cities[best_tour[i]]
                c_j = cities[best_tour[j]]
                c_j_next = cities[best_tour[(j + 1) % n]]

                d_old = euclidean_dist(c_i_prev, c_i) + euclidean_dist(c_j, c_j_next)
                d_new = euclidean_dist(c_i_prev, c_j) + euclidean_dist(c_i, c_j_next)

                if d_new < d_old - 1e-9:
                    best_tour[i:j + 1] = reversed(best_tour[i:j + 1])
                    cur_dist += (d_new - d_old)
                    history.append(cur_dist)
                    improved = True
                    break
            if improved:
                break
    return best_tour, history

# -------------------------------------------------------------------------
# 演算法 3: 爬山演算法 (First-Choice Hill Climbing)
# -------------------------------------------------------------------------
def solve_hill_climbing(cities, max_iterations=5000, seed=42):
    random.seed(seed)
    n = len(cities)
    current_tour = list(range(n))
    random.shuffle(current_tour)
    current_dist = compute_total_distance(current_tour, cities)
    history = [current_dist]

    for _ in range(max_iterations):
        i, j = sorted(random.sample(range(n), 2))
        neighbor = current_tour[:i] + current_tour[i:j + 1][::-1] + current_tour[j + 1:]
        neighbor_dist = compute_total_distance(neighbor, cities)

        if neighbor_dist < current_dist:
            current_tour = neighbor
            current_dist = neighbor_dist
            history.append(current_dist)

    return current_tour, history

# -------------------------------------------------------------------------
# 演算法 4: 模擬退火法 (Simulated Annealing)
# -------------------------------------------------------------------------
def solve_simulated_annealing(cities, initial_temp=1000.0, cooling_rate=0.995, min_temp=1e-3, seed=42):
    random.seed(seed)
    n = len(cities)
    current_tour = list(range(n))
    random.shuffle(current_tour)
    current_dist = compute_total_distance(current_tour, cities)

    best_tour = list(current_tour)
    best_dist = current_dist
    history = [best_dist]
    temp = initial_temp

    while temp > min_temp:
        i, j = sorted(random.sample(range(n), 2))
        neighbor = current_tour[:i] + current_tour[i:j + 1][::-1] + current_tour[j + 1:]
        neighbor_dist = compute_total_distance(neighbor, cities)
        delta = neighbor_dist - current_dist

        if delta < 0 or math.exp(-delta / temp) > random.random():
            current_tour = neighbor
            current_dist = neighbor_dist
            if current_dist < best_dist:
                best_tour = list(current_tour)
                best_dist = current_dist
                history.append(best_dist)

        temp *= cooling_rate

    return best_tour, history

# -------------------------------------------------------------------------
# 演算法 5: 梯度下降法 (離散最陡下降法 / Steepest Descent)
# -------------------------------------------------------------------------
def solve_steepest_descent(cities, seed=42):
    random.seed(seed)
    n = len(cities)
    current_tour = list(range(n))
    random.shuffle(current_tour)
    current_dist = compute_total_distance(current_tour, cities)
    history = [current_dist]

    while True:
        best_delta = 0.0
        best_swap = None

        for i in range(1, n - 1):
            for j in range(i + 1, n):
                c_i_prev = cities[current_tour[i - 1]]
                c_i = cities[current_tour[i]]
                c_j = cities[current_tour[j]]
                c_j_next = cities[current_tour[(j + 1) % n]]

                d_old = euclidean_dist(c_i_prev, c_i) + euclidean_dist(c_j, c_j_next)
                d_new = euclidean_dist(c_i_prev, c_j) + euclidean_dist(c_i, c_j_next)
                delta = d_new - d_old

                if delta < best_delta:
                    best_delta = delta
                    best_swap = (i, j)

        if best_swap is not None and best_delta < -1e-9:
            i, j = best_swap
            current_tour[i:j + 1] = reversed(current_tour[i:j + 1])
            current_dist += best_delta
            history.append(current_dist)
        else:
            break

    return current_tour, history

# -------------------------------------------------------------------------
# 繪圖視覺化函式
# -------------------------------------------------------------------------
def plot_results(cities, results):
    # 支援繁體中文標籤顯示
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()

    colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd', '#ff7f0e']

    # 1. 前 5 格繪製各演算法最終路徑
    for idx, (name, (tour, history, dist, elapsed)) in enumerate(results.items()):
        ax = axes[idx]
        x_pts = [cities[node][0] for node in tour] + [cities[tour[0]][0]]
        y_pts = [cities[node][1] for node in tour] + [cities[tour[0]][1]]

        ax.plot(x_pts, y_pts, marker='o', markersize=5, color=colors[idx], linewidth=1.5, alpha=0.85)
        ax.scatter([cities[tour[0]][0]], [cities[tour[0]][1]], color='red', s=70, zorder=5, label='起點')

        # 標記節點編號
        for node_id, (cx, cy) in enumerate(cities):
            ax.annotate(str(node_id), (cx, cy), textcoords="offset points", xytext=(0, 4), ha='center', fontsize=8)

        ax.set_title(f"{name}\n距離: {dist:.2f} | 耗時: {elapsed*1000:.1f}ms", fontsize=11, fontweight='bold')
        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.grid(True, linestyle='--', alpha=0.5)

    # 2. 第 6 格繪製收斂過程比較圖
    ax_conv = axes[5]
    for idx, (name, (_, history, _, _)) in enumerate(results.items()):
        # 將歷程步驟歸一化為相對進度比率，方便並列比較
        steps = list(range(len(history)))
        ax_conv.plot(steps, history, marker='.', label=name, color=colors[idx], linewidth=1.5)

    ax_conv.set_title("各演算法優化收斂過程", fontsize=11, fontweight='bold')
    ax_conv.set_xlabel("更新次數 (Improvement Steps)", fontsize=10)
    ax_conv.set_ylabel("路徑總長度", fontsize=10)
    ax_conv.legend(fontsize=8, loc='upper right')
    ax_conv.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------------
# 主執行程序
# -------------------------------------------------------------------------
if __name__ == "__main__":
    cities = generate_cities(num_cities=20, seed=42)
    results = {}

    # 1. 貪婪演算法
    t0 = time.perf_counter()
    tour_greedy, hist_greedy = solve_greedy(cities)
    t_greedy = time.perf_counter() - t0
    results["貪婪演算法"] = (tour_greedy, hist_greedy, compute_total_distance(tour_greedy, cities), t_greedy)

    # 2. 改良法 (以貪婪解為初始解)
    t0 = time.perf_counter()
    tour_2opt, hist_2opt = solve_2opt(tour_greedy, cities)
    t_2opt = time.perf_counter() - t0
    results["改良法 (2-opt)"] = (tour_2opt, hist_2opt, compute_total_distance(tour_2opt, cities), t_2opt)

    # 3. 爬山演算法
    t0 = time.perf_counter()
    tour_hc, hist_hc = solve_hill_climbing(cities, max_iterations=8000, seed=42)
    t_hc = time.perf_counter() - t0
    results["爬山演算法"] = (tour_hc, hist_hc, compute_total_distance(tour_hc, cities), t_hc)

    # 4. 模擬退火法
    t0 = time.perf_counter()
    tour_sa, hist_sa = solve_simulated_annealing(cities, seed=42)
    t_sa = time.perf_counter() - t0
    results["模擬退火法"] = (tour_sa, hist_sa, compute_total_distance(tour_sa, cities), t_sa)

    # 5. 梯度下降法 (最陡下降)
    t0 = time.perf_counter()
    tour_sd, hist_sd = solve_steepest_descent(cities, seed=42)
    t_sd = time.perf_counter() - t0
    results["梯度下降法 (最陡)"] = (tour_sd, hist_sd, compute_total_distance(tour_sd, cities), t_sd)

    # 終端機摘要輸出
    print(f"{'演算法名稱':<24} | {'總路徑長度':<12} | {'耗時 (ms)':<10}")
    print("-" * 52)
    for name, (_, _, dist, elapsed) in results.items():
        print(f"{name:<22} | {dist:<12.2f} | {elapsed*1000:<10.2f}")

    # 執行繪圖
    plot_results(cities, results)