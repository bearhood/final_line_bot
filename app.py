# import flask related
from flask import Flask, request, abort
from urllib.parse import parse_qsl
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage,
    VideoSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction,
    PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn,
    ImageCarouselTemplate, ImageCarouselColumn, FlexSendMessage,ImageMessage
)
import json
import random
import string
# create flask server
app = Flask(__name__)
line_bot_api = LineBotApi('xEScQDpvwHpdqPL2IW+VWIaybckiJf+eOjNaWgL/NlnfPqHpr0/FgrbM3SGSYThIvyGEz+nhDv6YudTI60ZbUQZy5NY4/KL+lAzPke/9P+Xi7MJEKj/uB9Jk4mAZquOVtxOBrYjtbNhYydDqhMo5YgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f36e10cfaec43f9fd321ba84f0ccfd7b')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

#歡迎訊息(區塊一)已經在Line developer網頁那設定好了

#以下是提前設定好方程和內容#########################

def details_template(name): #這個是傳出圖片後，彈出的按鈕，給對方選擇想看這個政治人物的什麼訊息
    template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            thumbnail_image_url='https://creazilla-store.fra1.digitaloceanspaces.com/emojis/42646/man-office-worker-emoji-clipart-md.png',
            title='想知道關於他的什麼呢？',
            text='關於'+name+'的訊息',
            actions=[
                PostbackAction(
                    label='政見',
                    display_text='我想知道'+name+'的政見',
                    data='action=顯示政見'
                ),
                PostbackAction(
                    label='資歷',
                    display_text='我想知道'+name+'的資歷',
                    data='action=顯示資歷'
                ),
                PostbackAction(
                    label='不感興趣了',
                    display_text='我不感興趣了',
                    data='action=回到首頁'
                )
            ]
        )
        )
    return template

def information(politician_name): #輸入他的名字，輸出他的資訊，剩下的靠你們了
    政見='他的政見'
    資歷='他的資歷'
    return [政見,資歷]

def others_template():
    template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            thumbnail_image_url='https://creazilla-store.fra1.digitaloceanspaces.com/emojis/42646/man-office-worker-emoji-clipart-md.png',
            title='想知道關於我們的什麼呢？',
            text='其他訊息',
            actions=[
                PostbackAction(
                    label='關於作者',
                    display_text='我想知道作者的資訊',
                    data='action=顯示作者資訊'
                ),
                URIAction(
                    label='軟體網站',
                    display_text='我想知道這機器人的官方網站',
                    uri='https://www.google.com/?gws_rd=ssl'
                    ),
                PostbackAction(
                    label='不感興趣了',
                    display_text='我不感興趣了',
                    data='action=回到首頁'
                )
            ]
        )
        )
    return template

#################################################

#區塊二和三，建議從這邊開始看
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # get user info & message
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='image': #如果訊息是圖片的話，做以下步驟
        image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4)) #生成圖檔名字
        image_content = line_bot_api.get_message_content(event.message.id)
        image_name = image_name.upper()+'.jpg'
        path='./static/'+image_name
        with open(path, 'wb') as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk) #在這裡把圖檔存起來了，在static資料夾裡
        policitian_name='someone' #我不知道你會怎麼處理，反正就是傳政治家的名字
        messages=[]
        messages.append(TextSendMessage(text='他的名字是：'+policitian_name),)
        messages.append(details_template(policitian_name))
        line_bot_api.reply_message(event.reply_token, messages)
        #print(postback_data.get('action'))

    # get msg details
    print('img from [', user_name, '](', user_id, ') ')
    
@handler.add(PostbackEvent) #有注意到details_message的按鈕上有"data=action=某某某"的部分嗎，那就是拿來觸發postback的事件
def handle_postback(event,politician_name):
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    # print(event.postback.data)
    postback_data = dict(parse_qsl(event.postback.data))
    # print(postback_data.get('action', ''))
    # print(postback_data.get('item', ''))
    sticker_list=[(1070, 17839), (6362, 11087920), (11537, 52002734), (8525, 16581293)]
    info=information(politician_name)
    if postback_data.get('action')=='顯示政見':
        messages=[]
        messages.append(TextSendMessage(text=f'他的政見為:\n{info[0]}'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='顯示資歷':
        messages=[]
        messages.append(TextSendMessage(text=f'他的資歷為:\n{info[1]}'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='回到首頁':
        messages=[]
        messages.append(TextSendMessage(text='請傳給我您有興趣的政治家的照片，或者打”其他”找其他資訊'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='顯示作者資訊':
        messages=[]
        messages.append(TextSendMessage(text='我們是中央大學的學生，作者有:王本偉、田家瑋、官慶睿、林泓宇、林恩立、李恆緯'))
        line_bot_api.reply_message(event.reply_token, messages)

@handler.add(MessageEvent, message=TextMessage)
def text_message(event):
    # get user info & message
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='text': #如果訊息是文字的話，做以下步驟
        receive_text=event.message.text
        if receive_text=='其他':
            messages=others_template()
            print('1')
            line_bot_api.reply_message(event.reply_token, messages)
            print('2')
        else:
            messages=TextSendMessage(text='請傳給我您有興趣的政治家的照片，或者打”其他”找其他資訊')
            line_bot_api.reply_message(event.reply_token, messages)


    # get msg details
    print('img from [', user_name, '](', user_id, ') ')


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5566)