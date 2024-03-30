# encoding:utf-8
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
thread_pool = ThreadPoolExecutor(max_workers=20)
from flask import Flask, request,Response
from flask import jsonify
from channel import channel_factory
from common.log import logger
from config import conf
import time
from threading import Thread
import requests
from message_process import wechat_account_channel_map,wechat_account_qr_map,wechat_account_callback_url_map,wechat_account_wx_user_id_map
channel_name="wx"
from bridge.context import *
from bridge.reply import *
# wechat_account_qr_img_map = {}
def validate_custom_user_id(custom_user_id):
    if custom_user_id is None or custom_user_id == "" or isinstance(custom_user_id,int):
        return ResponseCustom(code=500,message="自定义用户为空或者未设置")
    
class ResponseCustom():
    """_summary_
    封装一个返回成功的类
    Returns:
        _type_: _description_
    """
    def __init__(self, success=True, code=200, message=None, data=None):
        self.success = success
        self.code = code
        self.message = message
        self.data = data

    def to_json(self):
        return jsonify({
            "success": self.success,
            "code": self.code,
            "message": self.message,
            "data": self.data
        })

def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        print(conf["frequency_penalty"])
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)

def get_channel(channel_name, custom_user_id:str):
    channel = channel_factory.create_channel(channel_name, custom_user_id)
    return channel
    
def parse_wx_friends(data:list)->list:
    """_summary_
    解析微信返回的朋友列表
    Args:
        data (list): _description_

    Returns:
        list: _description_
    """
    return_list = []
    if len(data)>0:
        for item in data:
            return_list.append(
                {
                    "city":item["City"],
                    "headImgUrl":item["HeadImgUrl"],
                    "nickName":item["NickName"],
                    "province":item["Province"],
                    "signature":item["Signature"],
                    "wxUserId":item["UserName"]
                })
        return return_list
    else:
        return []

def parse_wx_groups(data:list)->list:
    """_summary_
    解析微信群组返回消息
    Args:
        data (list): _description_

    Returns:
        list: _description_
    """
    return_list = []
    if len(data)>0:
        for item in data:
            return_list.append(
                {
                    "city":item["City"],
                    "headImgUrl":item["HeadImgUrl"],
                    "nickName":item["NickName"],
                    "groupId":item["UserName"],
                    "selfWxUserId":item["Self"]["UserName"]
                })
    return return_list       
        
# 创建Flask应用实例
app = Flask(__name__)
@app.route('/api/wechat/create/qr', methods=['POST'])
def create_qr():
    """_summary_
    创建二维码
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    channel = get_channel(channel_name,custom_user_id)
    # thread_pool.submit(channel.startup)
    Thread(target=channel.startup).start()
    return ResponseCustom(message="创建微信登录二维码成").to_json()
    
@app.route('/api/wechat/get/qr', methods=['POST'])   
def get_qr():
    """_summary_
    获取二维码
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    # res=requests.post("http://127.0.0.1:5000/api/wechat/create/qr",json={
    #     "custom_user_id":custom_user_id
    # })
    # if res.json()["code"]==200:
    qr_img = wechat_account_qr_map[custom_user_id]
    return Response(qr_img, mimetype="image/png")

@app.route('/api/wechat/get/customUserWxUserId', methods=['POST'])
def get_custom_user_wx_user_id():
    """_summary_
    获取自定义用户对应的微信用户ID
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    wx_user_id = wechat_account_wx_user_id_map[custom_user_id]
    data={
        "customUserId": custom_user_id,
        "wxUserId": wx_user_id
    }
    return ResponseCustom(message="获取自定义用户ID对应的微信用户ID成功",data=data).to_json()
    
@app.route('/api/wechat/get/customUserWxFriends', methods=['POST'])
def get_custom_user_wx_friends():
    """_summary_
    获取自定义用户对应的微信所有朋友
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    wx_friends = wechat_account_channel_map[custom_user_id].get_friends()
    data={
        "customUserId": custom_user_id,
        "wxFriends": parse_wx_friends(wx_friends)
    }
    return ResponseCustom(message="获取自定义用户ID对应的微信好友成功",data=data).to_json()
    
@app.route('/api/wechat/get/customUserWxGroups', methods=['POST'])
def get_custom_user_wx_groups():
    """_summary_
    获取自定义用户对应的微信所有朋友
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    wx_groups = wechat_account_channel_map[custom_user_id].get_chatrooms()
    data={
        "customUserId": custom_user_id,
        "wxGroups": parse_wx_groups(wx_groups)
    }
    return ResponseCustom(message="获取自定义用户ID对应的微信群组成功",data=data).to_json()

@app.route('/api/wechat/post/message/wxUser', methods=['POST'])
def post_message_to_wx_user():
    """_summary_
    发送消息给微信用户
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    text = data.get("text",None)
    # wx_user_id = data.get("wxUserId",None)
    wx_receiver_user_id = data.get("wxReceiverUserId")
    message_type = data.get("messageType",None)
    
    wx_channel = wechat_account_channel_map[custom_user_id]
    if message_type == ReplyType.TEXT.value:
        reply = Reply(ReplyType.TEXT,text)
        context = Context()
        context.kwargs={"receiver":wx_receiver_user_id}
    wx_channel.send(reply, context)
    return ResponseCustom(message="发送消息给用户成功").to_json()
    
@app.route('/api/wechat/post/message/wxGroup', methods=['POST'])
def post_message_to_wx_group():
    """_summary_
    发送消息给微信群组
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    
    text = data.get("text",None)
    # wx_user_id = data.get("wxUserId",None)
    wx_receiver_group_id = data.get("wxReceiverGroupId")
    message_type = data.get("messageType",None)
    wx_channel = wechat_account_channel_map[custom_user_id]
    if message_type == ReplyType.TEXT.value:
        reply = Reply(ReplyType.TEXT,text)
        context = Context()
        context.kwargs={"receiver":wx_receiver_group_id}
    wx_channel.send(reply, context)
    return ResponseCustom(message="发送消息给群组成功").to_json()

@app.route('/api/wechat/delete/quit', methods=['POST'])
def delete_wx_user():
    """_summary_
    删除自定义用户登录的微信
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("customUserId",None)
    validate_custom_user_id(custom_user_id)
    channel = wechat_account_channel_map[custom_user_id]
    channel.login_out()
    del channel
    return ResponseCustom(message="删除自定义用户登录的微信成功").to_json()


if __name__ == "__main__":
    # run()
    app.run(threaded=True)
