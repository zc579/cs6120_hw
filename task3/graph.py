import matplotlib.pyplot as plt
import numpy as np

# 剔除result中超过10000的数据
filtered_df = df[df['result'] <= 10000]

# 按照benchmark和run列进行分组，并获取result列的值
grouped = filtered_df.groupby(['benchmark', 'run'])['result'].first().unstack()

# 设置图形参数
num_benchmarks = len(grouped.index)
num_runs = len(grouped.columns)
width = 0.8 / num_runs
index = np.arange(num_benchmarks)

# 创建画布
fig, ax = plt.subplots(figsize=(12, 6))

# 绘制柱状图
for i, run in enumerate(grouped.columns):
    ax.bar(index + i * width, grouped[run], width, label=run)

# 设置标签和标题
ax.set_xlabel('benchmark')
ax.set_ylabel('result')
ax.set_title('不同benchmark和run组合的result值（剔除超过10000的数据）')
ax.set_xticks(index + width * (num_runs - 1) / 2)
ax.set_xticklabels(grouped.index, rotation=45, fontsize=6)

# 显示图例
ax.legend()

# 显示图形
plt.tight_layout()
plt.show()