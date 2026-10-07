# 方法 1
def power2n(n):
    return 2**n

# 方法 2a：用遞迴
def power2n(n):
    return power2n(n-1)+power2n(n-1)

# 方法2b：用遞迴
def power2n(n):
    return 2*power2n(n-1)

# 方法 3：用遞迴+查表
def power2n(n, memo={}):
    if n in memo:
        return memo[n]
    if n == 0:
        return 1
    result = power2n(n-1)+power2n(n-1)
    memo[n] = result
    return result 



print('power2n(100)=', power2n_c(100))