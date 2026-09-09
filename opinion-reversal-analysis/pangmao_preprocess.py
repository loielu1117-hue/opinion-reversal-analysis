import pandas as pd
import glob

# 读取所有胖猫事件的CSV文件
files = glob.glob("zhihu_data_胖猫1/*.csv") + glob.glob("zhihu_data_胖猫2/*.csv") + glob.glob("zhihu_data_胖猫3/*.csv")
df_list = [pd.read_csv(f) for f in files]
df = pd.concat(df_list, ignore_index=True)

# 查看数据概览
print(df.shape)
print(df.columns)
print(df.head())
# 示例清洗
import re

def clean_html(text):
    if isinstance(text, str):
        return re.sub(r'<[^>]+>', '', text)
    return text

df['回答内容'] = df['回答内容'].apply(clean_html)
df = df.dropna(subset=['回答内容'])
df = df[df['回答内容'].str.len() > 10]  # 去除过短回答
df = df.drop_duplicates(subset=['回答ID'])  # 按回答ID去重
df['发布时间'] = pd.to_datetime(df['发布时间'])
df['发布日期'] = df['发布时间'].dt.date
print("合并后原始行数:", len(df))
print("清洗后行数:", len(df))
print("去重后行数:", len(df))
print("去除时间解析失败后行数:", len(df))
for f in files:
    temp = pd.read_csv(f, encoding='utf-8-sig')
    print(f"{f}: {len(temp)} 行")
# 保存到单个文件，方便后续分析
df.to_csv('zhihu_pangmao_cleaned.csv', index=False, encoding='utf-8-sig')
print("数据已保存")