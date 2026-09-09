import requests
import pandas as pd
import time
import random
import json
from datetime import datetime
from fake_useragent import UserAgent
import os


class ZhihuSpider:
    def __init__(self, cookie_str=None):
        """
        初始化知乎爬虫
        :param cookie_str: 知乎登录后的Cookie字符串（必填！）
        """
        self.ua = UserAgent()
        self.session = requests.Session()

        # 基础请求头 - 修改版：去掉Accept-Encoding，添加必要头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 去掉Accept-Encoding，避免返回压缩内容
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.zhihu.com/question/654859896',  # 可根据需要动态修改
            'Cookie': cookie_str,
            'x-requested-with': 'fetch',  # 关键头，模拟异步请求
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
        }
        self.session.headers.update(self.headers)

    def get_cookie_instructions(self):
        """打印获取Cookie的指引"""
        print("=" * 60)
        print("【重要】请按以下步骤获取知乎Cookie：")
        print("1. 用Chrome浏览器打开 https://www.zhihu.com")
        print("2. 登录你的知乎账号（必须登录！）")
        print("3. 按F12打开开发者工具 → Network（网络）标签")
        print("4. 刷新页面，找到第一个请求（通常是 www.zhihu.com）")
        print("5. 在 Request Headers 里找到 'Cookie:' 这一行")
        print("6. 右键 → 复制值 → 复制整个Cookie字符串")
        print("7. 粘贴到代码开头的 COOKIE_STR 变量中")
        print("=" * 60)

    def test_cookie(self, question_id=654859896):
        """测试Cookie是否有效，请求一个问题的一页回答"""
        url = f"https://www.zhihu.com/api/v4/questions/{question_id}/answers?limit=1"
        try:
            resp = self.session.get(url, timeout=10)
            print("状态码:", resp.status_code)
            print("响应头:", dict(resp.headers))
            print("返回内容预览:", resp.text[:200])
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print("JSON解析成功，包含数据：", "data" in data)
                except:
                    print("返回的不是JSON格式")
            else:
                print("请求失败")
        except Exception as e:
            print("测试异常:", e)

    def get_question_info(self, question_id):
        """
        获取问题基本信息
        :param question_id: 知乎问题ID（例如 123456789）
        :return: 问题标题等
        """
        url = f"https://www.zhihu.com/api/v4/questions/{question_id}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'title': data.get('title', ''),
                    'created': data.get('created', ''),
                    'answer_count': data.get('answer_count', 0)
                }
        except:
            pass
        return None

    def crawl_answers(self, question_id, max_answers=None, with_comments=False):
        """
        爬取问题下的所有回答
        :param question_id: 知乎问题ID
        :param max_answers: 最多爬取多少条回答（None表示全部）
        :param with_comments: 是否同时爬取评论
        :return: DataFrame
        """
        print(f"\n🔍 开始爬取问题：{question_id}")

        # 先获取问题信息
        q_info = self.get_question_info(question_id)
        if q_info:
            print(f"   标题：{q_info['title']}")
            print(f"   总回答数：{q_info['answer_count']}")

        all_answers = []
        offset = 0
        limit = 20  # 知乎API每页20条
        page = 1

        while True:
            try:
                # 随机延迟 2-4秒 —— 防封
                delay = random.uniform(2, 4)
                print(f"   第{page}页 (offset={offset})，等待{delay:.1f}秒...")
                time.sleep(delay)

                # 知乎回答API
                url = f"https://www.zhihu.com/api/v4/questions/{question_id}/answers"
                params = {
                    'include': 'data[*].is_normal,content,excerpt,created_time,updated_time,voteup_count,comment_count,author',
                    'limit': limit,
                    'offset': offset,
                    'sort_by': 'default'
                }

                resp = self.session.get(url, params=params, timeout=15)

                # 检查是否被重定向到登录页
                if resp.url.startswith('https://www.zhihu.com/signin'):
                    print("   ❌ Cookie失效或未登录，请重新获取Cookie")
                    self.get_cookie_instructions()
                    break

                if resp.status_code != 200:
                    print(f"   ❌ 请求失败，状态码：{resp.status_code}")
                    break

                # 尝试解析JSON
                try:
                    data = resp.json()
                except:
                    print("   ❌ 返回的不是JSON格式，可能被反爬。响应头：", dict(resp.headers))
                    print("   返回内容预览:", resp.text[:200])
                    break

                answers = data.get('data', [])

                if not answers:
                    print("   没有更多回答了")
                    break

                print(f"   ✅ 本页获取 {len(answers)} 条回答")

                for ans in answers:
                    # 提取作者信息
                    author = ans.get('author', {})
                    author_name = author.get('name', '匿名用户')
                    author_id = author.get('url_token', '')

                    # 回答内容（纯文本）
                    content = ans.get('content', '')
                    # 简单清理HTML标签（如果需要纯文本可以用BeautifulSoup进一步处理）

                    answer_item = {
                        '问题ID': question_id,
                        '回答ID': ans.get('id'),
                        '作者昵称': author_name,
                        '作者ID': author_id,
                        '回答内容': content,
                        '发布时间': datetime.fromtimestamp(ans.get('created_time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        '更新時間': datetime.fromtimestamp(ans.get('updated_time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        '点赞数': ans.get('voteup_count', 0),
                        '评论数': ans.get('comment_count', 0),
                        '采集时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    all_answers.append(answer_item)

                    # 如果需要爬取评论（可选）
                    if with_comments and ans.get('comment_count', 0) > 0:
                        answer_id = ans.get('id')
                        comments = self.crawl_comments(answer_id, max_comments=50)
                        # 这里可以单独保存评论，或者关联存储
                        if comments:
                            # 你可以选择将评论保存到另一个文件
                            pass

                # 检查是否还有下一页
                pagination = data.get('paging', {})
                if not pagination.get('is_end', True):
                    offset += limit
                    page += 1
                else:
                    print("   已到达最后一页")
                    break

                # 如果设置了最大回答数且已达到
                if max_answers and len(all_answers) >= max_answers:
                    print(f"   已达到最大回答数限制 ({max_answers})")
                    break

            except Exception as e:
                print(f"   ❌ 处理异常：{e}")
                break

        print(f"🎉 采集完成！共获得 {len(all_answers)} 条回答")
        return pd.DataFrame(all_answers)

    def crawl_comments(self, answer_id, max_comments=100):
        """
        爬取某个回答下的评论（可选功能）
        :param answer_id: 回答ID
        :param max_comments: 最大评论数
        :return: DataFrame
        """
        # 知乎评论API
        url = f"https://www.zhihu.com/api/v4/answers/{answer_id}/comments"
        params = {
            'limit': 20,
            'offset': 0,
            'order': 'normal'
        }

        all_comments = []
        while len(all_comments) < max_comments:
            try:
                time.sleep(random.uniform(1, 2))
                resp = self.session.get(url, params=params)
                if resp.status_code != 200:
                    break

                data = resp.json()
                comments = data.get('data', [])
                if not comments:
                    break

                for cmt in comments:
                    author = cmt.get('author', {})
                    comment_item = {
                        '回答ID': answer_id,
                        '评论ID': cmt.get('id'),
                        '作者昵称': author.get('name', ''),
                        '作者ID': author.get('url_token', ''),
                        '评论内容': cmt.get('content', ''),
                        '发布时间': datetime.fromtimestamp(cmt.get('created_time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        '点赞数': cmt.get('vote_count', 0)
                    }
                    all_comments.append(comment_item)

                pagination = data.get('paging', {})
                if not pagination.get('is_end', True):
                    params['offset'] += 20
                else:
                    break

            except:
                break

        return pd.DataFrame(all_comments)

    def save_to_csv(self, df, event_name, question_id):
        """
        保存数据到CSV
        """
        # 创建输出目录
        output_dir = f"zhihu_data_{event_name}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/question_{question_id}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 数据已保存至：{filename}")
        return filename


# ====================== 使用示例 ======================
if __name__ == "__main__":
    # 🔥【第一步】填写你的知乎Cookie（必须！）
    # 按照指引获取Cookie，粘贴到下面的引号中（注意去掉中文说明，确保以 _zap= 开头）
    COOKIE_STR = r"_zap=2c85f14a-2ded-4e0a-9f5d-440e55992821; d_c0=sYPU2EIo1xuPTmH4JEm5NJ5Z7DKyQ83bVcM=|1771075427; captcha_session_v2=2|1:0|10:1771075428|18:captcha_session_v2|88:QW01NTB0MVNBUE9WVlBTT0lDdnViMjF6Y0xZb1hkeWxxSXQ4akNGRWVWaWVIelBrZzhick9RNkhqYk45eHBsZw==|41f5f0f6c929b7b4703018a88f78b15d14d568f1f65541aa1877c1249897b201; __snaker__id=grQPfyRCbaGrjew1; gdxidpyhxdE=40tSZEJRRfd3EnC5d2I7MaRpNVH3YOrIzS9TbB3f0fkibAkqIulcgprUJP%5C3LWd54Vj%5CVVovnTyPhPbiTxHhNP4f13ny%2FysYzs%2Bw3U8CqXUEfTnZa%5C%2BnYs%2BlUVW3Zj9Qo0ZkhfwvpBvQuV55G4ny9Zs1oygYfGsw8YAgsaMXWX%2F4zmg%5C%3A1771076330484; q_c1=13e411dc8c39491d9b1ea899d6a56acd|1771075445000|1771075445000; z_c0=2|1:0|10:1771076713|4:z_c0|92:Mi4xdmJLQlhRQUFBQUN4ZzlUWVFpalhHeVlBQUFCZ0FsVk5kTVY5YWdCdllxOFJCTS11Q3l5ZS1HM0lJVHlqSklobEZ3|617f1ca3b1ccccd3229ef45ca188af4f2f11e58cc165e8b91916d9b233935ba8; __zse_ck=005_ixKUbarSgw0zd42rqtcoHK1/Q6ojOIuMh=NpmpeJW4=bX6uoosLuqT7KIrHQikZr1Mkt6wmD5nZ20DIqTHQixh/IsSphAp22KYjKs9V1PI5pyahh04mIW37qAoIqvCpZ-BahsQo1WsIsP3d693Z9a3zuJDPPTbRKW1wWfxCNRBmKpdThcgOV1qBAvd4l1CuqXN6vNip7rrXsVJbP94IKtMInxmhtaA0s5Q8uVFD0PVkpTNaRkY5Hlg3vBaDIc3SmO; _xsrf=01e47079-5575-4ed2-a262-b4bebb57240e; SESSIONID=fLOo8QseGlAEQuCAn4v1AqUWwBvIwOSahM91GVTSTmP; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1771075429,1772198642; HMACCOUNT=1B46C312142407EB; JOID=WlEXBE5IYowjOFYbAkhKEol8ccATLyXGTg0GY2ICD8Zjay5ZSLP2KkU0XBUFTcUwl76YMhBzyK1eoUz4WLubjcU=; osd=VFAdA0JGY4YkNFgaCE9GHIh2dswdLi_BQgMHaWUOAcdpbCJXSbnxJks1VhIJQ8Q6kLKWMxp0xKNfq0v0VrqRisk=; BEC=04678b89b8500afc30b012aad143c9b0; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1772198790"
    # 如果没有Cookie，打印指引
    if not COOKIE_STR:
        spider = ZhihuSpider()
        spider.get_cookie_instructions()
        exit()

    # 初始化爬虫
    spider = ZhihuSpider(cookie_str=COOKIE_STR)

    # 先测试Cookie是否有效
    print("=== 测试Cookie有效性 ===")
    spider.test_cookie()  # 默认测试问题654859896
    print("=== 测试结束 ===\n")

    # 🔥【第二步】设置你要爬取的事件和问题ID
    # 你需要在知乎上找到与事件相关的高热度问题
    events_questions = [
        {"event": "李明德1", "question_id": 8763622322, "max_answers": 500},
        {"event": "李明德2", "question_id": 1934260780020233321, "max_answers": 500},
        {"event": "李明德3", "question_id":12138305773, "max_answers": 500},
        {"event": "李明德4", "question_id": 8726283851, "max_answers": 500},
        {"event": "李明德5", "question_id": 12138305773, "max_answers": 500},
    ]

    # 循环爬取
    for eq in events_questions:
        print(f"\n========== 开始采集事件：【{eq['event']}】问题ID：{eq['question_id']} ==========")

        # 爬取回答
        df = spider.crawl_answers(
            question_id=eq['question_id'],
            max_answers=eq.get('max_answers'),
            with_comments=False  # 如果需要评论可以改为True，但会慢很多
        )

        if not df.empty:
            spider.save_to_csv(df, eq['event'], eq['question_id'])

        # 事件之间间隔10秒
        if eq != events_questions[-1]:
            print("\n⏳ 等待10秒，准备采集下一个问题...")
            time.sleep(10)

    print("\n🎉 全部采集完成！")