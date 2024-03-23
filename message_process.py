from bridge.context import *
from bridge.reply import *
import time
wechat_account_map={}
wechat_account_url_map={}
from app import wechat_account_map
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
    print(wechat_account_map)
    item = wechat_account_map["user_id"]
    item.send(reply, context)
