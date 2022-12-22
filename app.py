# import flask related
from api_keys import line_bot_api, handler


from flask import Flask, request, abort
from urllib.parse import parse_qsl
# import linebot related

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

import urllib.parse
import json
import random
import string
import sqlite3
# create flask server
from flask import Flask, render_template 



app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/service')
def show_service_detail():
    return render_template('service.html')

@app.route('/ai')
def index1():
    return render_template('ai.html')

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
    print('name==',name)
    dir = 'https://github.com/bearhood/final_line_bot/raw/main/data/db_person_pic/'
    template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            
            thumbnail_image_url= dir+'{}.jpg'.format(urllib.parse.quote(name) ),
            title='想知道關於他的什麼呢？',
            text='關於'+name+'的訊息',
            actions=[
                PostbackAction(
                    label='政見',
                    display_text='我想知道'+name+'的政見',
                    data='action=顯示政見&politician_name={}'.format(name)
                ),
                PostbackAction(
                    label='資歷',
                    display_text='我想知道'+name+'的資歷',
                    data='action=顯示資歷&politician_name={}'.format(name)
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

def func_fetching( cur, name ):
    '''
    此處為調閱候選人的資料的函數:  cur 為檔案的指標, name 為候選人的姓名
    回傳為 list：
    ex:
        [{'單位': '臺北市第8屆市長',
            '號次': 6,
            '姓名': '蔣萬安',
            '生日': '67 年 12 月 26 日',
            '政見': '大家好我叫蔣萬安'}]

    '''
    querydata = cur.execute('''SELECT * FROM candidate WHERE `姓名` = '{}';'''.format(name))
    result_value = [ i for i in querydata ]
    result_name = (description[0] for description in querydata.description )
    result = [ dict( zip(result_name,data) ) for data in result_value ]
    print( result)
    return result
def information(politician_name): #輸入他的名字，輸出他的資訊，剩下的靠你們了
    print('politician==',politician_name)
    con = sqlite3.connect('./data/db_text/main_v3.db')
    cur = con.cursor()
    政見=''
    資歷=''
    politi_info = func_fetching( cur, politician_name )
    print( politi_info)

    if( len( politi_info ) != 0 ):
        資歷=politi_info[0]['經歷']
        政見=politi_info[0]['政見']
    else:
        print( "No one is fitted")
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

#接收 所有圖片訊息
import cv2
def face_detect_demo( img ):
    name = ['張家豪',
            '王文娟',
            '鄭匡宇',
            '黃聖峰',
            '童文薰',
            '蔣萬安',
            '蘇煥智',
            '黃珊珊',
            '施奉先',
            '唐新民',
            '謝立康',
            '陳時中']
    cascade_path = r'.\data\db_cv2NET\haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    recog = cv2.face.LBPHFaceRecognizer_create()         # 啟用訓練人臉模型方法
    recog.read(r'.\data\db_cv2NET\face.yml')                            # 讀取人臉模型檔
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 轉換成黑白
    faces = face_cascade.detectMultiScale(gray,1.1)  # 追蹤人臉 ( 目的在於標記出外框 )
    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)            # 標記人臉外框
        idnum,confidence = recog.predict(gray[y:y+h,x:x+w])  # 取出 id 號碼以及信心指數 confidence
        if confidence < 60:
            text = name[int(idnum)-1]                               # 如果信心指數小於 60，取得對應的名字
        else:
            text = '???'                                          # 不然名字就是 ???
        # 在人臉外框旁加上名字
        cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
        if text == name[int(idnum)-1]:
            print(text)
            return (text, img)
    return(text,img)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # get user info & message
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='image': #如果訊息是圖片的話，做以下步驟
        image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4)) #生成圖檔名字
        image_content = line_bot_api.get_message_content(event.message.id)
        image_name = image_name.upper()+'.jpg'
        path='./result/origin/'+image_name
        
        with open(path, 'wb') as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk) #在這裡把圖檔存起來了，在static資料夾裡
        received_img = cv2.imread(path)
        print( 'path = ',path)
        policitian_name,img = face_detect_demo( received_img )
        cv2.imwrite('./result/processed/{}'.format(image_name),img )
        # policitian_name='someone' #我不知道你會怎麼處理，反正就是傳政治家的名字
        messages=[]
        if( policitian_name !='???' ):
            messages.append(TextSendMessage(text='他的名字是：'+policitian_name))
            messages.append(details_template(policitian_name))
        else:
            messages.append(TextSendMessage(text='抱歉！辨識不出來是誰'))

        line_bot_api.reply_message(event.reply_token, messages)
        #print(postback_data.get('action'))

    # get msg details
    print('img from [', user_name, '](', user_id, ') ')

# 以下為所有接收到按鈕後的集散地
@handler.add(PostbackEvent) #有注意到details_message的按鈕上有"data=action=某某某"的部分嗎，那就是拿來觸發postback的事件
def handle_postback(event):
    
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    # print(event.postback.data)
    postback_data = dict(parse_qsl(event.postback.data))
    politician_name = postback_data.get('politician_name')
    # print(postback_data.get('action', ''))
    # print(postback_data.get('item', ''))
    sticker_list=[(1070, 17839), (6362, 11087920), (11537, 52002734), (8525, 16581293)]
    info=information(politician_name)
    print('handle_postback__name = ' , politician_name)
    if postback_data.get('action')=='顯示政見':
        messages=[]
        if( info[0]== 'img'):
            dir = 'https://github.com/bearhood/final_line_bot/raw/main/data/db_pic/'
            url = dir+'{}.jpg'.format(urllib.parse.quote(politician_name) )
            print(url)
            messages.append(ImageSendMessage(original_content_url=url,
                                             preview_image_url=url))
        else:
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


# 我猜應該是接收所有文字的集散地
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
        elif( '我想知道:' in receive_text ):
            con = sqlite3.connect('./data/db_text/main_v3.db')
            cur = con.cursor()

            
            messages=[]
            politicitian_name = receive_text.split(':')[-1]

            data = func_fetching(cur, politicitian_name)
            if( len( data ) != 0 ):
                messages.append(TextSendMessage(text='他的名字是：'+politicitian_name),)
                messages.append(details_template(politicitian_name))
                line_bot_api.reply_message(event.reply_token, messages)
            else:
                messages.append(TextSendMessage(text='資料庫裡面沒有：'+politicitian_name),)
                line_bot_api.reply_message(event.reply_token, messages)
        else:
            messages=TextSendMessage(text='請傳給我您有興趣的政治家的照片，或者打”其他”找其他資訊')
            line_bot_api.reply_message(event.reply_token, messages)

    # get msg details
    print('img from [', user_name, '](', user_id, ') ')


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5566)