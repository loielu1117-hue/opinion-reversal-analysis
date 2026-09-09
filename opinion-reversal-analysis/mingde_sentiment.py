import pandas as pd
import time
from snownlp import SnowNLP

df = pd.read_csv('zhihu_limingde_cleaned.csv')  # 正确的输入文件
df['发布时间'] = pd.to_datetime(df['发布时间'])

def get_sentiment_snownlp(text):
    try:
        s = SnowNLP(str(text)[:1000])
        return s.sentiments
    except:
        return 0.5

print("开始情感分析，共", len(df), "条...")
sentiment_scores = []
batch_size = 100
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]['回答内容'].tolist()
    scores = [get_sentiment_snownlp(text) for text in batch]
    sentiment_scores.extend(scores)
    print(f"已处理 {i+len(batch)}/{len(df)} 条")
    time.sleep(0.5)

df['情感得分'] = sentiment_scores
df.to_csv('zhihu_limingde_with_sentiment.csv', index=False, encoding='utf-8-sig')
print("情感分析完成，已保存")