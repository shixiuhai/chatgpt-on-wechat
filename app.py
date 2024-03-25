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

# def start_channel(channel_name: str):
#     channel = channel_factory.create_channel(channel_name)
#     print("------------------------")
#     channel.startup()
#     print("+++++++++++++++++")
#     print(channel.qr_img)
#     print("+++++++++++++++++++")
    
    # while True:
    #     time.sleep(1)
    # while channel.user_id is None:
    #     time.sleep(1)
    #     print("循环中")
    #     # channel.startup()
    #     if channel.qr_img is not None:
    #         wechat_account_qr_img_map["qr"] = channel.qr_img
    #     if channel.user_id is not None:
    #         wechat_account_map[channel.user_id] = channel
        
            
            
    # print("==========添加到map里成功=========")
    # print(wechat_account_map)
    # print("==========添加到map里成功=========")
def get_channel(channel_name, custom_user_id:str):
    channel = channel_factory.create_channel(channel_name, custom_user_id)
    return channel
    
    

# def run():
#     try:
#         # ctrl + c
#         sigterm_handler_wrap(signal.SIGINT)
#         # kill signal
#         sigterm_handler_wrap(signal.SIGTERM)
#         channel_name = "wx"
#         start_channel(channel_name)
#         while True:
#             time.sleep(1)
#     except Exception as e:
#         logger.error("App startup failed!")
#         logger.exception(e)
        
        
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
    custom_user_id = data.get("custom_user_id",None)
    validate_custom_user_id(custom_user_id)
    # thread_pool.submit(start_channel,channel_name)
    channel = get_channel(channel_name,custom_user_id)
    # thread_pool.submit(channel.startup)
    Thread(target=channel.startup).start()
    return ResponseCustom(message="创建微信登录二维码成").to_json()
    # while "qr" not in wechat_account_qr_img_map:
    #     print(wechat_account_qr_img_map)
        
    #     time.sleep(1)
    # return Response(wechat_account_qr_img_map["qr"], mimetype="image/png")
    # qr_img = start_channel(channel_name)
    # qr_byte = wechat_account_login_qr_map["qr"]
    # channel = channel_factory.create_channel(channel_name)
    # thread_pool.submit(channel.startup)
    # while channel.qr_img is not None:
    #     time.sleep(1)
    # return Response(channel.qr_img, mimetype="image/png")

@app.route('/api/wechat/get/qr', methods=['POST'])   
def get_qr():
    """_summary_
    获取二维码
    Returns:
        _type_: _description_
    """
    data = request.get_json(silent=True)
    custom_user_id = data.get("custom_user_id",None)
    validate_custom_user_id(custom_user_id)
    # res=requests.post("http://127.0.0.1:5000/api/wechat/create/qr",json={
    #     "custom_user_id":custom_user_id
    # })
    # if res.json()["code"]==200:
    qr_img = wechat_account_qr_map[custom_user_id]
    return Response(qr_img, mimetype="image/png")
    
@app.route('/api/post', methods=['POST'])
def post_api():
    # 获取 POST 请求参数
    data = request.get_json(silent=True)
    name = data['name']
    age = data['age']

    # 处理数据
    # ...

    # 返回响应
    return {"success": True, "message": "success"}

@app.route('/api/get', methods=['GET'])
def get_api():
    # 获取 GET 请求参数
    name = request.args.get('name')
    age = request.args.get('age')

    # 处理数据
    # ...

    # 返回响应
    return {"success": True, "message": "success"}



if __name__ == "__main__":
    # run()
    app.run(threaded=True)
