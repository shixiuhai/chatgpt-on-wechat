# encoding:utf-8
import signal
import sys
import time
from channel import channel_factory
from common.log import logger
from config import conf
from message_process import wechat_account_map


def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)

def start_channel(channel_name: str):
    channel = channel_factory.create_channel(channel_name)
    wechat_account_map["user_id"]=channel
    print("==========添加到map里成功=========")
    print(wechat_account_map)
    channel.startup()

def run():
    try:
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)
        channel_name = "wx"
        start_channel(channel_name)
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)

if __name__ == "__main__":
    run()
