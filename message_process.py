from bridge.context import *
from bridge.reply import *
import time
wechat_account_map={}
wechat_account_callback_url_map={}
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
    item = wechat_account_map['@83b067d420dad8e6b2655a350f09f06e535c3ede60cb2a7e8f30716aa2d7daf7']
    item.send(reply, context)
