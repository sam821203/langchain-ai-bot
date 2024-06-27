from flask import Flask, render_template, url_for
from flask import request
from configparser import ConfigParser
import google.generativeai as genai

# 讀取配置文件
config = ConfigParser()
config.read("config.ini")

# 配置 Google Generative AI API
genai.configure(api_key=config["Gemini"]["API_KEY"])

from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 初始化 Generative Model，設置安全性和生成配置
llm = genai.GenerativeModel(
    "gemini-1.5-flash-latest",
    safety_settings={
        # 設置對不同類型的有害內容的處理閾值
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
    generation_config={
        # 設置生成文本的配置
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    },
)

 # 啟動聊天，初始化歷史記錄
chat = llm.start_chat(history=[])

# 角色描述，用於聊天開始時的設置
role = """
    妳是一個二十五歲的年輕女性，喜歡跳舞和逛藝術展覽。
    妳聊天的目的是為了請對方送妳一份禮物。
    以下是對方問的問題，你直接用這個角色回答就好，不用再舉例。
"""

app = Flask(__name__)

@app.route("/")
def home():
    # 主頁面路由，返回index.html
    return render_template("index.html")

@app.route("/call_llm", methods=["POST"])
def call_llm():
    # 處理 POST 請求，與 Generative Model 進行互動
    if request.method == "POST":
        print("POST!")
        # 獲取 POST 數據
        data = request.form
        print(data)
        to_llm = ""
        if len(chat.history) > 0:
            # 如果有歷史記錄，直接使用用戶輸入
            to_llm = data["message"]
        else:
            # 如果無歷史記錄，添加角色描述
            to_llm = role + data["message"]
        try:
            # 向 Generative Model 發送消息
            result = chat.send_message(to_llm)
        except Exception as e:
            print(e)
            return "我媽來了，她說不能聊這個(雙手比叉)"
        print(chat.history)
        # 移除結果字符串末尾的換行符 \n
        return result.text.replace("\n", "")