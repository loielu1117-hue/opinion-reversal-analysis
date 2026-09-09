import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ========== 1. 读取数据 ==========
df = pd.read_csv('zhihu_limingde_with_sentiment.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
df = df.dropna(subset=['发布时间'])
print(f"原始数据总量：{len(df)}")

# ========== 2. 年份分布 ==========
df['年份'] = df['发布时间'].dt.year
year_counts = df['年份'].value_counts().sort_index()
print("每年数据量：")
print(year_counts)

# ========== 3. 只保留2025年数据 ==========
df = df[df['发布时间'].dt.year == 2025]
print(f"\n2025年数据量：{len(df)}")

# ========== 4. 情感得分清洗 ==========
print("\n情感得分描述统计（清洗前）：")
print(df['情感得分'].describe())
df = df[(df['情感得分'] >= 0) & (df['情感得分'] <= 1)]
print("情感得分描述统计（清洗后）：")
print(df['情感得分'].describe())

# ========== 5. 按日聚合（核心修正：这里包含了 std） ==========
daily = df.groupby(df['发布时间'].dt.date)['情感得分'].agg(['mean', 'std', 'count']).reset_index()
daily.columns = ['日期', '情感均值', '情感标准差', '回答数']
daily['日期'] = pd.to_datetime(daily['日期'])

# ========== 6. 绘制双轴图（情感均值±标准差 + 回答数柱状图） ==========
fig, ax1 = plt.subplots(figsize=(16, 6))

# 左轴：情感均值与标准差带
color1 = 'tab:blue'
ax1.set_xlabel('日期')
ax1.set_ylabel('情感得分', color=color1)
ax1.plot(daily['日期'], daily['情感均值'], 'o-', color=color1, markersize=3, label='日均情感得分')
ax1.fill_between(daily['日期'],
                 daily['情感均值'] - daily['情感标准差'],
                 daily['情感均值'] + daily['情感标准差'],
                 alpha=0.2, color=color1, label='±1标准差')
ax1.axvline(x=pd.Timestamp('2025-02-13'), color='red', linestyle='--', linewidth=2, label='反转日 (2月13日)')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_ylim(0, 1)
ax1.grid(True, alpha=0.3)

# 右轴：回答数柱状图
color2 = 'tab:orange'
ax2 = ax1.twinx()
ax2.bar(daily['日期'], daily['回答数'], alpha=0.3, color=color2, width=1.5, label='每日回答数')
ax2.set_ylabel('回答数', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

# 设置横轴范围（可根据实际数据调整）
ax1.set_xlim(pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31'))
plt.title('李明德事件情感演化时序图')

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

fig.tight_layout()
plt.savefig('李明德事件情感演化时序图.png', dpi=300)
plt.show()

# ========== 7. 输出每日统计信息（前10行） ==========
print("\n每日统计信息（前10行）：")
print(daily.head(10))

# ========== 8. 按月聚合（用于论文表格） ==========
df['月份'] = df['发布时间'].dt.to_period('M')
monthly = df.groupby('月份')['情感得分'].agg(['mean', 'std', 'count']).reset_index()
monthly.columns = ['月份', '情感均值', '情感标准差', '回答数']
print("\n每月统计信息（修正后，标准差不为0）：")
print(monthly)

# 可选：保存月度统计到CSV
monthly.to_csv('李明德事件月度统计.csv', index=False, encoding='utf-8-sig')
print("\n月度统计已保存至 '李明德事件月度统计.csv'")