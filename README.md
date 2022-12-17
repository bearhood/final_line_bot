# final_line_bot

請注意：已經屏蔽掉
api_keys.py

以下為 api_keys.py 的內容:

from linebot import (
    LineBotApi, WebhookHandler
)

line_bot_api = LineBotApi('')


handler = WebhookHandler('')

以上

# 請自行建立一份在子資料夾！！

## 進度：
2022/12/17
19：44 田家瑋筆
目前完成文字的搜索

可透過 輸入 我想知道: ... 進行搜索


經歷都只會是文字，政見較複雜，

若 該候選人只有提供圖片版的政見，則回傳圖片
若 有文字版則回傳文字版
