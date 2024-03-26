from bridge.context import *
from bridge.reply import *
import time
wechat_account_wx_user_id_map={} # 微信用户ID存储
wechat_account_qr_map={} # 二维码
wechat_account_channel_map={} # 微信实体类
wechat_account_callback_url_map={} # 配置用户的回调接口

def process_user_message( ctype: ContextType, content, **kwargs)->None:
    print(content)
    print(kwargs)
    if kwargs["isgroup"] == True:
        return
    
    context = Context(ctype, content)
    context.kwargs = kwargs
    print("==========接受的信息=============")
    print(context)
    print("==========接受的信息=============")
    reply = Reply(ReplyType.TEXT,"回复你的哟")
    context = Context()
    context.kwargs={"receiver":kwargs["msg"].from_user_id}
    print(context)
    print(wechat_account_channel_map)
    item = wechat_account_channel_map["123"]
    item.send(reply, context)
