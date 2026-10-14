# 方法 2a：用遞迴
def power2n(n):
    if n == 0:
        return 1
    return power2n(n-1)+power2n(n-1)

print('power2n(100)=', power2n(100))