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
from message_process import wechat_account_map
# wechat_account_qr_img_map = {}
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

def start_channel(channel_name: str):
    channel = channel_factory.create_channel(channel_name)
    channel.startup()
    print("+++++++++++++++++")
    print(channel.qr_img)
    print("+++++++++++++++++++")
    
    while True:
        time.sleep(1)
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
@app.route('/api/wechat/login', methods=['POST'])
def wechat_login():
    channel_name="wx"
    thread_pool.submit(start_channel,channel_name)
    return "sucessful"
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
    app.run()
