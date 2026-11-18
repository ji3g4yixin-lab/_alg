import numpy as np
import itertools
import time

# ==============================================================================
# 1. 用數值方法來算單變數微分和積分
# ==============================================================================
def diff_1d(f, x, h=1e-5):
    """單變數數值微分 (中央差分法)"""
    return (f(x + h) - f(x - h)) / (2 * h)

def integral_1d_riemann(f, a, b, n=10000):
    """單變數數值積分 (中點黎曼和)"""
    dx = (b - a) / n
    # 取每個區間的中點來計算，精確度比左/右端點法更高
    midpoints = a + (np.arange(n) + 0.5) * dx
    return np.sum([f(x) for x in midpoints]) * dx

# ==============================================================================
# 2. 用蒙地卡羅法來算單變數積分
# ==============================================================================
def integral_1d_mc(f, a, b, samples=100000):
    """單變數蒙地卡羅積分"""
    x = np.random.uniform(a, b, samples)
    y = np.array([f(val) for val in x])
    return (b - a) * np.mean(y)

# ==============================================================================
# 3. 用數值方法來算 n 變數微分(梯度)和積分(超體積)
# ==============================================================================
def gradient_nd(f, x, h=1e-5):
    """n 變數數值微分 (計算梯度向量)"""
    x = np.array(x, dtype=float)
    grad = np.zeros_like(x)
    for i in range(len(x)):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
    return grad

# ==============================================================================
# 5. 請用黎曼積分法，寫函數 integral(f, low, high) 來做 n 變數積分 (同時涵蓋第3題的n維積分)
# ==============================================================================
def integral_riemann(f, low, high, bins_per_dim=None):
    """
    n 變數黎曼積分 (中點法)
    low, high: 長度為 n 的陣列或串列
    bins_per_dim: 每個維度要切幾等分 (若為 None 則根據維度自動調整避免當機)
    """
    low = np.array(low, dtype=float)
    high = np.array(high, dtype=float)
    dim = len(low)
    
    # 維度災難保護機制：限制總網格數不超過 1,000,000 點
    if bins_per_dim is None:
        if dim == 1:
            bins_per_dim = 10000
        elif dim == 2:
            bins_per_dim = 500      # 500^2 = 250,000 點
        elif dim == 5:
            bins_per_dim = 12       # 12^5 = 248,832 點
        else:
            # 對於超高維度 (如 100 維)，即便每維只切 2 份也有 2^100 點，無法暴力遍歷
            print(f"  [警告] 維度高達 {dim} 維，黎曼網格法遭遇「維度災難」(網格數呈指數爆炸)！")
            print(f"  [降級處理] 僅示範每維切 1 份 (中點近似) 以避免程式當機...")
            bins_per_dim = 1

    dx = (high - low) / bins_per_dim
    cell_volume = np.prod(dx) # 每個超立方體微元的體積
    
    # 建立每個維度的中點座標
    axes = [low[i] + (np.arange(bins_per_dim) + 0.5) * dx[i] for i in range(dim)]
    
    total_sum = 0.0
    # 使用 itertools.product 遍歷所有 n 維網格點，節省記憶體
    for point in itertools.product(*axes):
        total_sum += f(np.array(point))
        
    return total_sum * cell_volume

# ==============================================================================
# 6. 請改用蒙地卡羅法，寫函數 integral(f, low, high) 來做 n 變數積分 (同時涵蓋第4題)
# ==============================================================================
def integral_mc(f, low, high, samples=200000):
    """
    n 變數蒙地卡羅積分
    low, high: 長度為 n 的陣列或串列
    """
    low = np.array(low, dtype=float)
    high = np.array(high, dtype=float)
    dim = len(low)
    
    # 計算積分區域的超體積 (Hypervolume)
    hypervolume = np.prod(high - low)
    
    # 一次生成 (samples, dim) 的均勻分布隨機點矩陣
    points = np.random.uniform(low, high, size=(samples, dim))
    
    # 計算所有隨機點的函數值 (支援向量化或逐點計算)
    try:
        # 嘗試直接向量化計算 (速度極快)
        values = f(points)
        if values.shape != (samples,):
            raise ValueError
    except Exception:
        # 若函數 f 不支援二維陣列輸入，則退回逐列計算
        values = np.array([f(p) for p in points])
        
    return hypervolume * np.mean(values)


# ==============================================================================
# 測試範例主程式
# ==============================================================================
if __name__ == "__main__":
    np.random.seed(42) # 固定隨機種子方便重現結果

    print("==========================================")
    print("【測試 1】單變數數值微分與積分")
    print("==========================================")
    # 測試函數: f(x) = x^2 + 2x + 1，在 x=3 時微分應為 8；在 [0, 3] 積分應為 21
    f_1d = lambda x: x**2 + 2*x + 1
    print(f"函數 f(x) = x^2 + 2x + 1")
    print(f"  在 x = 3 的微分 (解析解 = 8.0) : {diff_1d(f_1d, 3):.6f}")
    print(f"  在 [0, 3] 的黎曼積分 (解析解 = 21.0) : {integral_1d_riemann(f_1d, 0, 3):.6f}")

    print("\n==========================================")
    print("【測試 2】蒙地卡羅法算單變數積分")
    print("==========================================")
    print(f"  在 [0, 3] 的蒙地卡羅積分 (解析解 = 21.0) : {integral_1d_mc(f_1d, 0, 3):.6f}")

    print("\n==========================================")
    print("【測試 3 & 4】n 變數微分(梯度) 與 積分(超體積)")
    print("==========================================")
    # 測試函數: f(x, y, z) = x^2 + y^3 + 2z
    # 梯度為 [2x, 3y^2, 2]，在 (1, 2, 3) 處梯度應為 [2, 12, 2]
    f_3d = lambda p: p[0]**2 + p[1]**3 + 2*p[2]
    pt = [1.0, 2.0, 3.0]
    print(f"函數 f(x,y,z) = x^2 + y^3 + 2z 在 {pt} 的梯度:")
    print(f"  數值梯度 (解析解 = [2. 12. 2.]) : {gradient_nd(f_3d, pt)}")
    
    # 積分區間 [0, 1] x [0, 2] x [0, 1]
    # 解析解 = int_0^1 int_0^2 int_0^1 (x^2 + y^3 + 2z) dz dy dx = 16/3 ≈ 5.333333
    low_3d, high_3d = [0, 0, 0], [1, 2, 1]
    print(f"在 [0,1]x[0,2]x[0,1] 的超體積積分 (解析解 ≈ 5.333333):")
    print(f"  黎曼積分法   : {integral_riemann(f_3d, low_3d, high_3d, bins_per_dim=40):.6f}")
    print(f"  蒙地卡羅法   : {integral_mc(f_3d, low_3d, high_3d):.6f}")

    # 定義第 5 與 第 6 題的共同測試函數: f(x) = x_1^2 + x_2^2 + ... + x_n^2
    # 支援單點 (1D array) 與 批次點 (2D array) 輸入
    def sum_of_squares(x):
        x = np.asarray(x)
        if x.ndim == 1:
            return np.sum(x**2)
        return np.sum(x**2, axis=1)

    dims = [1, 2, 5, 100]

    print("\n==========================================")
    print("【測試 5】黎曼積分法計算 f(x) = x_1^2 + ... + x_n^2 (區間 [0, 1]^n)")
    print("==========================================")
    # 理論解析解: 每個維度 int_0^1 x_i^2 dx_i = 1/3，n 維相加即為 n / 3
    for d in dims:
        low = [0.0] * d
        high = [1.0] * d
        t0 = time.time()
        ans = integral_riemann(sum_of_squares, low, high)
        dt = time.time() - t0
        exact = d / 3.0
        print(f"  {d:3d} 維 | 黎曼積分 = {ans:10.6f} | 理論解 = {exact:10.6f} | 耗時 = {dt:.4f}s")

    print("\n==========================================")
    print("【測試 6】蒙地卡羅法計算 f(x) = x_1^2 + ... + x_n^2 (區間 [0, 1]^n)")
    print("==========================================")
    for d in dims:
        low = [0.0] * d
        high = [1.0] * d
        t0 = time.time()
        ans = integral_mc(sum_of_squares, low, high, samples=200000)
        dt = time.time() - t0
        exact = d / 3.0
        print(f"  {d:3d} 維 | 蒙地卡羅 = {ans:10.6f} | 理論解 = {exact:10.6f} | 耗時 = {dt:.4f}s")