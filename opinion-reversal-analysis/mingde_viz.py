import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False   # 用来正常显示负号
plt.close()  # 关闭图形，释放内存，程序会继续运行并退出

print("正在读取数据...")
# 1. 读取数据
df = pd.read_csv('zhihu_limingde_with_sentiment.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
df = df.dropna(subset=['发布时间'])
print("数据读取完成")

# 2. 数据清洗
df = df[(df['情感得分'] >= 0) & (df['情感得分'] <= 1)]
df = df[df['发布时间'].dt.year == 2025]
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
plt.axvline(x=pd.Timestamp('2025-02-13'), color='red', linestyle='--', label='反转日 (2月13日)')
plt.xlabel('日期')
plt.ylabel('情感标准差')
plt.title('李明德事件每日情感得分标准差（极化程度）')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(pd.Timestamp('2025-01-01'), pd.Timestamp('2025-05-31'))
plt.tight_layout()
plt.savefig('李明德情感标准差时序图.png', dpi=300)
print("情感标准差时序图已保存")