import os
## requirements： pip install transformers torch
from langchain.tools import tool
from transformers import pipeline

# 加载 HuggingFace 情感分析模型
pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

@tool("HF_Emotion_Recognition")
def hf_emotion_recognition_tool(text: str) -> str:
    """
    使用 HuggingFace tabularisai/multilingual-sentiment-analysis 模型进行情感强度分析，支持中文。
    返回情感类别和置信度。
    优点：情感分析比较准确。
    缺点：响应较慢，可能得挂梯子
    """
    try:
        result = pipe(text)
        if not result or not isinstance(result, list):
            return "未能识别出有效情绪。"
        label = result[0].get("label", "未知")
        score = result[0].get("score", 0)
        # 映射为强度分数
        label_map = {
            "Very Negative": "非常消极",
            "Negative": "消极",
            "Neutral": "中性",
            "Positive": "积极",
            "Very Positive": "非常积极"
        }
        zh_label = label_map.get(label, label)
        # intensity = int(round(score * 10))
        return f"情感类别: {zh_label}，（置信度: {score:.2f}）"
    except Exception as e:
        return f"HuggingFace情感分析调用失败: {e}"