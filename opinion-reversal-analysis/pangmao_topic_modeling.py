import pandas as pd
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = 'C:/Windows/Fonts/simhei.ttf'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False   # 用来正常显示负号
plt.close()  # 关闭图形，释放内存，程序会继续运行并退出

# 读取数据
df = pd.read_csv('zhihu_pangmao_cleaned.csv')
df['发布时间'] = pd.to_datetime(df['发布时间'])


# 分词函数
def chinese_cut(text):
    return ' '.join(jieba.cut(str(text)))


# 按反转日划分
reversal = pd.Timestamp('2024-05-19')
before = df[df['发布时间'] < reversal]['回答内容'].apply(chinese_cut).tolist()
after = df[df['发布时间'] >= reversal]['回答内容'].apply(chinese_cut).tolist()

print(f"反转前文本数：{len(before)}，反转后文本数：{len(after)}")


# 定义LDA建模函数
def lda_on_texts(texts, n_topics=5, n_words=10, name=''):
    if len(texts) < 10:
        print(f"{name} 文本太少，跳过")
        return
    vectorizer = CountVectorizer(max_features=1000,
                                 stop_words=['的', '了', '在', '是', '我', '他', '有', '这', '个', '也', '不', '就',
                                             '说', '人', '都', '到', '和'])
    X = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    feature_names = vectorizer.get_feature_names_out()
    print(f"\n===== {name} 主题 =====")
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_words - 1:-1]]
        print(f"主题{topic_idx + 1}: " + " ".join(top_words))

        # 可选：生成词云
        wordcloud = WordCloud(font_path='simhei.ttf', width=800, height=400, background_color='white').generate(
            ' '.join(top_words))
        plt.figure(figsize=(6, 3))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"{name} 主题{topic_idx + 1}")
        plt.savefig(f"{name}_topic{topic_idx + 1}.png", dpi=200)
        plt.close()


# 对反转前文本建模
lda_on_texts(before, n_topics=5, name='胖猫_反转前')

# 对反转后文本建模
lda_on_texts(after, n_topics=5, name='胖猫_反转后')