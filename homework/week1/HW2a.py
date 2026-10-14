# 方法 2a：用遞迴
def power2n(n):
    result = power2n(n-1)+power2n(n-1)
    return result

print('power2n(100)=', power2n(100))