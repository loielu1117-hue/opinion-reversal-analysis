import pandas as pd
from snownlp import SnowNLP
import time

# 读取清洗后的数据
df = pd.read_csv('zhihu_pangmao_cleaned.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'])

def get_sentiment_snownlp(text):
    """返回情感得分，范围 0~1，越接近1越正面"""
    try:
        # 文本过长会影响速度，可以截断
        s = SnowNLP(str(text)[:1000])
        return s.sentiments  # 返回0~1之间的情感倾向
    except:
        return 0.5  # 中性

# 分批处理，避免卡死
print("开始情感分析（SnowNLP），共", len(df), "条...")
sentiment_scores = []
batch_size = 100

for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]['回答内容'].tolist()
    scores = [get_sentiment_snownlp(text) for text in batch]
    sentiment_scores.extend(scores)
    print(f"已处理 {i+len(batch)}/{len(df)} 条")
    time.sleep(0.5)  # 稍微停顿，避免占用过高CPU

df['情感得分'] = sentiment_scores

# 保存结果
df.to_csv('zhihu_pangmao_with_sentiment.csv', index=False, encoding='utf-8-sig')
print("情感分析完成，已保存")