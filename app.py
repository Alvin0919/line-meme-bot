import os
import re
import random
import json

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

configuration = Configuration(
    access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
)
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET", ""))

# 載入梗圖資料
MEMES_PATH = os.path.join(os.path.dirname(__file__), "memes.json")
with open(MEMES_PATH, "r", encoding="utf-8") as f:
    memes = json.load(f)

total_count = len(memes)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 功能 4：使用說明
        if text in ("說明", "幫助", "help"):
            help_text = (
                "你好，我是稍有善根的機器人，以下是本機器人的使用說明。\n\n"
                "【使用說明】\n"
                "🔍 輸入關鍵字 → 搜尋相關台詞\n"
                "🔢 輸入 T+編號 → 取得圖片（例如 T3）\n"
                "🎲 輸入「抽」→ 隨機抽一張圖\n"
                "❓ 輸入「說明」→ 顯示本說明"
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=help_text)],
                )
            )
            return

        # 功能 5：全部台詞
        if text in ("全部台詞", "全部", "列表"):
            lines = [
                f"【T{str(m['id']).zfill(4)}】{m['description']}"
                for m in memes
            ]
            response = "📋 全部台詞一覽\n\n" + "\n".join(lines)
            response += f"\n\n共 {total_count} 筆，輸入編號取得圖片（例如 T3）"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)],
                )
            )
            return

        # 功能 3：隨機抽圖
        if text == "抽":
            meme = random.choice(memes)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageMessage(
                            original_content_url=meme["image_url"],
                            preview_image_url=meme["image_url"],
                        )
                    ],
                )
            )
            return

        # 功能 2：編號取圖（t + 數字）
        match = re.match(r"^[tT](\d+)$", text)
        if match:
            num = int(match.group(1))
            if 1 <= num <= total_count:
                meme = memes[num - 1]
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            ImageMessage(
                                original_content_url=meme["image_url"],
                                preview_image_url=meme["image_url"],
                            )
                        ],
                    )
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text=f"編號超出範圍！有效範圍：t1 ~ t{total_count}"
                            )
                        ],
                    )
                )
            return

        # 功能 1：關鍵字搜尋（比對 description + tags）
        keyword = text.lower()
        results = [
            m
            for m in memes
            if keyword in m["description"].lower()
            or keyword in m.get("tags", "").lower()
        ]

        if results:
            lines = [
                f"【T{str(m['id']).zfill(4)}】{m['description']}"
                for m in results[:20]
            ]
            response = "\n".join(lines)
            response += "\n\n💡 輸入編號即可取得圖片，例如 T3"
            if len(results) > 20:
                response += f"\n（共 {len(results)} 筆結果，僅顯示前 20 筆）"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)],
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="找不到相關梗圖，試試其他關鍵字吧！")
                    ],
                )
            )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
