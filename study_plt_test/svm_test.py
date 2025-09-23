import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 创建一维线性不可分数据
x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([0, 0, 1, 1, 0, 0])  # 标签：中间是1，两边是0

plt.figure(figsize=(15, 4))

# 左图：原始一维数据
plt.subplot(1, 3, 1)
plt.scatter(x[y==0], np.zeros_like(x[y==0]), c='red', s=100, label='类别 0')
plt.scatter(x[y==1], np.zeros_like(x[y==1]), c='blue', s=100, label='类别 1')
plt.xlabel('x')
plt.title('一维空间：线性不可分')
plt.legend()
plt.grid(True)

# 中图：映射到二维空间
plt.subplot(1, 3, 2)
# 定义一个简单的映射函数：φ(x) = (x, x²)
x_2d = x
y_2d = x ** 2  # 这就是核技巧：增加一个新维度 x²

plt.scatter(x_2d[y==0], y_2d[y==0], c='red', s=100, label='类别 0')
plt.scatter(x_2d[y==1], y_2d[y==1], c='blue', s=100, label='类别 1')

# 在二维空间中，我们可以画一条直线来分割
x_line = np.linspace(0, 7, 100)
y_line = -2*x_line + 12  # 一条分割直线
plt.plot(x_line, y_line, 'g-', linewidth=2, label='决策边界')

plt.xlabel('x')
plt.ylabel('x²')
plt.title('二维空间：变得线性可分')
plt.legend()
plt.grid(True)

# 右图：在原始空间中的决策边界
plt.subplot(1, 3, 3)
plt.scatter(x[y==0], np.zeros_like(x[y==0]), c='red', s=100, label='类别 0')
plt.scatter(x[y==1], np.zeros_like(x[y==1]), c='blue', s=100, label='类别 1')

# 将二维的直线边界投影回一维
# 二维直线：y = -2x + 12，代入 y = x²
# 得到：x² = -2x + 12 → x² + 2x - 12 = 0
roots = np.roots([1, 2, -12])
decision_point1, decision_point2 = roots[0], roots[1]

plt.axvline(x=decision_point1, color='green', linestyle='--', label='决策点')
plt.axvline(x=decision_point2, color='green', linestyle='--')

plt.xlabel('x')
plt.title('一维投影：非线性边界')
plt.legend()
plt.grid(True)

plt.tight_layout()

plt.show()


