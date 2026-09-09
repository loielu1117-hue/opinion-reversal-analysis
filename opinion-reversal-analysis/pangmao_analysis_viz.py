import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False   # 用来正常显示负号
plt.close()  # 关闭图形，释放内存，程序会继续运行并退出

df = pd.read_csv('zhihu_pangmao_with_sentiment.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
df = df.dropna(subset=['发布时间'])

# 提取年份
df['年份'] = df['发布时间'].dt.year

# 统计每年数据量
year_counts = df['年份'].value_counts().sort_index()
print("每年数据量：")
print(year_counts)

# 绘制按月的回答数分布（可选）
df['月份'] = df['发布时间'].dt.to_period('M')
month_counts = df['月份'].value_counts().sort_index()
print("\n每月数据量：")
print(month_counts)
# 只保留2024年数据
df = df[df['发布时间'].dt.year == 2024]

# 检查情感得分是否在0~1之间
print(df['情感得分'].describe())
# 如果有异常值，删除或修正
df = df[(df['情感得分'] >= 0) & (df['情感得分'] <= 1)]

# 按天聚合
daily = df.groupby(df['发布时间'].dt.date)['情感得分'].agg(['mean', 'std', 'count']).reset_index()
daily.columns = ['日期', '情感均值', '情感标准差', '回答数']
daily['日期'] = pd.to_datetime(daily['日期'])
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 6))
plt.plot(daily['日期'], daily['情感均值'], marker='o', linestyle='-', label='日均情感得分')
plt.axvline(x=pd.Timestamp('2024-05-19'), color='red', linestyle='--', label='反转日 (5月19日)')
plt.fill_between(daily['日期'],
                 daily['情感均值'] - daily['情感标准差'],
                 daily['情感均值'] + daily['情感标准差'],
                 alpha=0.2, label='±1标准差')

# 设置合理范围
plt.xlim(pd.Timestamp('2024-04-01'), pd.Timestamp('2024-12-31'))
plt.ylim(0, 1)

plt.xlabel('日期')
plt.ylabel('情感得分')
plt.title('胖猫事件情感演化时序图')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('情感演化时序图_最终版.png', dpi=300)
plt.show()