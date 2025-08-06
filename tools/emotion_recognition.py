import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool

# 加载 .env 文件中的环境变量
load_dotenv()

import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool

# 加载 .env 文件中的环境变量
load_dotenv()

@tool("Emotion_Recognition")
def emotion_recognition_tool(text: str) -> str:
    """
    调用百度NLP对话情绪识别API，返回一级和二级情绪标签及概率。
    """
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    if not api_key or not secret_key:
        return "未配置百度NLP API密钥，请在.env文件中添加 BAIDU_API_KEY 和 BAIDU_SECRET_KEY。"

    # 获取access_token
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    try:
        token_resp = requests.post(token_url, data=token_data, timeout=5)
        token_resp.raise_for_status()
        access_token = token_resp.json().get("access_token")
        if not access_token:
            return f"获取access_token失败，返回内容: {token_resp.text}"
    except Exception as e:
        return f"获取access_token时出错: {e}"

    # 对话情绪识别API
    emotion_url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/emotion?access_token={access_token}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "scene": "talk",
        "text": text
    }
    try:
        resp = requests.post(emotion_url, headers=headers, json=payload, timeout=5)
        print("百度对话情绪识别响应内容:", resp.text)  # 调试用
        resp.raise_for_status()
        result = resp.json()
        if "items" in result and result["items"]:
            item = result["items"][0]
            first_label_map = {
                "optimistic": "正向",
                "neutral": "中性",
                "pessimistic": "负向"
            }
            first_label = first_label_map.get(item.get("label", "neutral"), "未知")
            first_prob = item.get("prob", 0)
            subitems = item.get("subitems", [])
            sub_desc = []
            for sub in subitems:
                sub_label = sub.get("label", "未知")
                sub_prob = sub.get("prob", 0)
                replies = sub.get("replies", [])
                reply_text = f"，参考回复：{'；'.join(replies)}" if replies else ""
                sub_desc.append(f"{sub_label}({sub_prob:.2f}){reply_text}")
            sub_desc_str = "；".join(sub_desc) if sub_desc else "无细分情绪"
            return (
                f"用户当前情绪分析结果如下，包含情绪类别和对应的概率："
                f"一级情绪：{first_label}({first_prob:.2f})；"
                f"二级情绪：{sub_desc_str}"
            )
        else:
            return f"未能识别出有效情绪，返回内容: {resp.text}"
    except Exception as e:
        return f"情绪识别API调用失败: {e}, 返回内容: {resp.text if 'resp' in locals() else '无响应'}"

# @tool("Emotion_Recognition")
# def emotion_recognition_tool(text: str) -> str:
#     """
#     调用百度NLP情感倾向分析API，返回情绪类别和强度。
#     """
#     api_key = os.getenv("BAIDU_API_KEY")
#     secret_key = os.getenv("BAIDU_SECRET_KEY")
#     if not api_key or not secret_key:
#         return "未配置百度NLP API密钥，请在.env文件中添加 BAIDU_API_KEY 和 BAIDU_SECRET_KEY。"
#
#     # 获取access_token
#     token_url = "https://aip.baidubce.com/oauth/2.0/token"
#     token_data = {
#         "grant_type": "client_credentials",
#         "client_id": api_key,
#         "client_secret": secret_key
#     }
#     try:
#         token_resp = requests.post(token_url, data=token_data, timeout=5)
#         token_resp.raise_for_status()
#         access_token = token_resp.json().get("access_token")
#         if not access_token:
#             return f"获取access_token失败，返回内容: {token_resp.text}"
#     except Exception as e:
#         return f"获取access_token时出错: {e}"
#
#     # 情感倾向分析API
#     sentiment_url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={access_token}"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "text": text,
#         "charset": "UTF-8"
#     }
#     try:
#         resp = requests.post(sentiment_url, headers=headers, json=payload, timeout=5)
#         print("百度NLP响应内容:", resp.text)  # 调试用
#         resp.raise_for_status()
#         result = resp.json()
#         # if "items" in result and result["items"]:
#         #     item = result["items"][0]
#         #     sentiment_map = {0: "消极", 1: "中性", 2: "积极"}
#         #     sentiment = sentiment_map.get(item.get("sentiment", 1), "未知")
#         #     confidence = item.get("confidence", 0)
#         #     intensity = int(confidence * 10)
#         #     # 返回自然语言描述，便于Agent理解
#         #     return f"用户当前情绪类别为：{sentiment}，强度为：{intensity}/10。"
#         # else:
#         #     return f"未能识别出有效情绪，返回内容: {resp.text}"
#         if "items" in result and result["items"]:
#             item = result["items"][0]
#             sentiment_map = {0: "消极", 1: "中性", 2: "积极"}
#             sentiment = sentiment_map.get(item.get("sentiment", 1), "未知")
#             confidence = item.get("confidence", 0)
#             positive_prob = item.get("positive_prob", 0)
#             negative_prob = item.get("negative_prob", 0)
#
#             # 分别计算积极和消极强度
#             # positive_intensity = max(1, round(positive_prob * confidence * 10)) if positive_prob > 0.1 else 0
#             # negative_intensity = max(1, round(negative_prob * confidence * 10)) if negative_prob > 0.1 else 0
#
#             # return (
#             #     f"用户当前情绪分析结果如下："
#             #     f"属于积极情绪的概率：{positive_prob}，"
#             #     f"属于消极情绪的概率：{negative_prob}，"
#             #     f"主判定类别：{sentiment}（置信度：{confidence:.2f}）"
#             # )
#             def calculate_intensity(prob, base_sentiment):
#
#                 """动态权重强度计算：
#                 - 当基础情感匹配时：置信度强化主情感
#                 - 当基础情感不匹配时：仅使用概率值
#                 """
#                 weight = confidence if sentiment == base_sentiment else 0.5
#                 return min(10, int(round((prob * 0.7 + weight * 0.3) * 10)))
#
#             # 计算双情感强度
#             positive_intensity = calculate_intensity(positive_prob, "积极")
#             negative_intensity = calculate_intensity(negative_prob, "消极")
#
#             # 构建混合情感描述
#             emotion_desc = []
#             if positive_intensity >= 3:  # 强度阈值
#                 emotion_desc.append(f"积极强度{positive_intensity}/10")
#             if negative_intensity >= 3:
#                 emotion_desc.append(f"消极强度{negative_intensity}/10")
#
#             # 默认中性处理
#             if not emotion_desc:
#                 neutral_intensity = int(round((1 - abs(positive_prob - negative_prob)) * 5)) # 矛盾程度转化
#                 emotion_desc.append(f"中性强度{neutral_intensity}/10")
#
#             return (
#             f"情感类别: {sentiment} (置信度{confidence:.2f}), "
#             f"混合情感: {'+'.join(emotion_desc)}")
#         else:
#             return f"未能识别出有效情绪，返回内容: {resp.text}"
#     except Exception as e:
#         return f"情绪识别API调用失败: {e}, 返回内容: {resp.text if 'resp' in locals() else '无响应'}"