import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False   # 用来正常显示负号

print("正在读取数据...")
# 1. 读取数据
df = pd.read_csv('zhihu_pangmao_with_sentiment.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
df = df.dropna(subset=['发布时间'])
print("数据读取完成")

# 2. 数据清洗
df = df[(df['情感得分'] >= 0) & (df['情感得分'] <= 1)]
df = df[df['发布时间'].dt.year == 2024]
print(f"有效数据量：{len(df)}")
print(f"时间范围：{df['发布时间'].min()} 至 {df['发布时间'].max()}")

# 3. 按天聚合
daily = df.groupby(df['发布时间'].dt.date)['情感得分'].agg(['mean', 'std', 'count']).reset_index()
daily.columns = ['日期', '情感均值', '情感标准差', '回答数']
daily['日期'] = pd.to_datetime(daily['日期'])

# 4. 绘制情感标准差时序图
print("绘制情感标准差时序图...")
plt.figure(figsize=(12, 5))
plt.plot(daily['日期'], daily['情感标准差'], marker='o', color='orange', label='情感标准差')
plt.axvline(x=pd.Timestamp('2024-05-19'), color='red', linestyle='--', label='反转日 (5月19日)')
plt.xlabel('日期')
plt.ylabel('情感标准差')
plt.title('胖猫事件每日情感得分标准差（极化程度）')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(pd.Timestamp('2024-04-01'), pd.Timestamp('2024-07-31'))
plt.tight_layout()
plt.savefig('情感标准差时序图.png', dpi=300)
print("情感标准差时序图已保存")

# 5. 绘制按周的箱线图
print("准备箱线图数据...")
df['周'] = df['发布时间'].dt.to_period('W').astype(str)
df_plot = df[(df['发布时间'] >= '2024-04-01') & (df['发布时间'] <= '2024-07-31')]
print(f"箱线图数据量：{len(df_plot)}")

print("绘制箱线图...")
plt.figure(figsize=(14, 6))
df_plot.boxplot(column='情感得分', by='周', grid=False)
plt.axvline(x=5.5, color='red', linestyle='--', label='反转周')  # 需手动调整
plt.title('胖猫事件情感得分分布（按周）')
plt.suptitle('')
plt.xlabel('周')
plt.ylabel('情感得分')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('情感得分箱线图.png', dpi=300)
print("箱线图已保存")

# 可选：如果不需要交互显示，可以不加 plt.show()
# plt.show()  # 如果你希望看到窗口，可以取消注释，但要记得关闭窗口

# 6. 输出统计信息
print("\n每日统计信息（前10行）：")
print(daily.head(10))
print("\n每日标准差的基本统计：")
print(daily['情感标准差'].describe())
print("所有任务完成！")
fig, ax1 = plt.subplots(figsize=(12,5))
ax1.plot(daily['日期'], daily['情感标准差'], 'o-', color='orange', label='情感标准差')
ax1.set_xlabel('日期')
ax1.set_ylabel('情感标准差', color='orange')
ax1.tick_params(axis='y', labelcolor='orange')
ax1.axvline(pd.Timestamp('2024-05-19'), color='red', linestyle='--', label='反转日')

ax2 = ax1.twinx()
ax2.bar(daily['日期'], daily['回答数'], alpha=0.3, color='gray', label='回答数')
ax2.set_ylabel('回答数', color='gray')
ax2.tick_params(axis='y', labelcolor='gray')

plt.title('胖猫事件：情感标准差与每日回答数')
fig.tight_layout()
plt.savefig('标准差与回答数.png', dpi=300)
plt.show()