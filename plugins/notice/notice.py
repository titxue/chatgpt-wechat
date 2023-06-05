# encoding:utf-8

import os
import sys
import time
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from lib import itchat
# from myUtils import MysqldbHelper
import json
import re
import requests

from plugins.notice.myUtils import MysqldbHelper

@plugins.register(
    name="notice",
    desire_priority=-1,
    hidden=True,
    desc="公告",
    version="0.1",
    author="lxue",
)
class Notice(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Notice] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return

        content = e_context["context"].content
        # logger.info(e_context)
        # logger.info(e_context["context"])
        logger.info(content)


        if content == "开启公告":
            logger.info("开启公告")
            # 定义数据库访问参数
            config = {
                'host': '58.87.69.208',
                'port': 3306,
                'user': 'root',
                'passwd': 'lxue0422',
                'charset': 'utf8'
            }
            # 初始化打开数据库连接
            mydb = MysqldbHelper(config)
            # 打印数据库版本
            mydb.createDataBase("nft")
            # get_notice(mydb)
            # 以下是为了让程序不结束，如果有用于PyQt等有主循环消息的框架，可以去除下面代码
            
            try:
                while True:
                    self.get_notice(mydb)
                    time.sleep(1)
            except KeyboardInterrupt:
                sys.exit()





    def get_help_text(self, **kwargs):
        help_text = "输入Hello，我会回复你的名字\n输入End，我会回复你世界的图片\n"
        return help_text

    def get_millisecond(self):
        """
        :return: 获取精确毫秒时间戳,13位
        """
        
        millis = int(round(time.time() * 1000))
        return str(millis)
    
    def get_notice(self, db):
        heads = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Version/13.0.3 Mobile/15E148 Safari/604.1 "
        }  # 要用自己的user-agent
        # 在下面的代码行中使用断点来调试脚本。
        flag = False
        proxies = {"http": None, "https": None}
        res = requests.get("https://info.18art.art/html/infor/infor.html?sub=0&v=" + self.get_millisecond(), heads, proxies=proxies)
        res.encoding = "utf-8"
        re_obj = re.compile("injectJson=(.*?);")
        text = re_obj.findall(res.text)[0]
        notice_list = json.loads(text)
        for i in notice_list["noticeList"]:
            # for j in i["list"]:
            #     insert_sql = "insert into notice(id, class_id, class_name,cover_img,time,title,url) values('%s', %s, '%s'," \
            #                  "'%s',%s," \
            #                  "'%s','%s')" % (
            #                      j["id"], j["classId"], j["className"], j["coverImg"], j["time"],
            #                      j["title"],
            #                      j["url"])
            #     time.sleep(1)
            #     mydb.executeSql(insert_sql)
            i_by_time = sorted(i["list"], key=lambda x: x["time"], reverse=True)
            # print(i)


            # 判断i_by_time 是否为空
            if not i_by_time:
                continue
            
            last = i_by_time[0]
            # print(last)
            # if last["classId"] == 8:
            #     continue
            # old = mydb.executeSql("SELECT * FROM notice WHERE id = '%s'" % last["id"])
            
            try:
                old =  db.select("notice", cond_dict = {'id':str(last["id"])})
                flag = True
            except:
                logger.warn("查询出错跳过当前")
                flag = False
                continue
            if not old and flag==True:
                # print(old)
                insert_sql = "insert into notice(id, class_id, class_name,cover_img,time,title,url) values('%s', %s, '%s'," \
                            "'%s',%s," \
                            "'%s','%s')" % (
                                last["id"], last["classId"], last["className"], last["coverImg"], last["time"],
                                last["title"],
                                last["url"])
                

                # 下面是@两个人的发送例子，room_wxid, at_list需要自己替换'44674383098@chatroom', 'wxid_ym97mp5eia9x22', 
                logger.info("发现新公告") 
                content="%s----%s----%s"%(last["className"],last["title"],last["url"])
                curdir = os.path.dirname(__file__)
                config_path = os.path.join(curdir, "config.json")
                gconf = None
                if not os.path.exists(config_path):
                    gconf = {"group_name_white_list": []}
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(gconf, f, indent=4)
                else:
                    with open(config_path, "r", encoding="utf-8") as f:
                        gconf = json.load(f)
                
                if gconf["group_name_white_list"]:
                    group_name_white_list = gconf["group_name_white_list"]
                    for group in group_name_white_list:
                        self.SendChatRoomsMsg(group, u"@%s\u2005%s"%("所有人",content))
                    # self.SendChatRoomsMsg("chat", content)
                    # self.SendChatRoomsMsg("动物园2.0", content)
                # wechat.send_room_at_msg(to_wxid="21022638855@chatroom",
                #             content="%s{$@}----%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_zxxyr7t1fnzw12'])
                # wechat.send_room_at_msg(to_wxid="39089525796@chatroom",
                #             content="%s{$@}----%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_irpufrgztlqs21'])
                # wechat.send_room_at_msg(to_wxid="44734292127@chatroom",
                #             content="%s{$@}----%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_1odjguf35j9u22'])
                # wechat.send_room_at_msg(to_wxid="43784291946@chatroom",
                #             content="%s{$@}----%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_irpufrgztlqs21'])
                # wechat.send_room_at_msg(to_wxid="48171062567@chatroom",
                #             content="%s{$@}----%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_odw2p4ot00kn22'])
                # wechat.send_room_at_msg(to_wxid="44674383098@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['sunyunlian1278'])
                # wechat.send_room_at_msg(to_wxid="44014099853@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_jg8ru97yrqyd22'])   
                # wechat.send_room_at_msg(to_wxid="47840157257@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_2d7abqt2pok322']) 
                # wechat.send_room_at_msg(to_wxid="19327054671@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['fgtaixuyi']) 
                # wechat.send_room_at_msg(to_wxid="47838668525@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_bp4212ih9o7822']) 
                # wechat.send_room_at_msg(to_wxid="38775038702@chatroom",
                #             content="%s{$@}---%s----%s"%(last["className"],last["title"],last["url"]),
                #             at_list=['wxid_2xl9uh7ouid422']) 
                db.executeSql(insert_sql)


    def SendChatRoomsMsg(self, gname, context):
        # 获取群组所有的相关信息（注意最好群聊保存到通讯录）
        myroom = itchat.get_chatrooms(update=True)
        # myroom = itchat.get_chatrooms()
        #定义全局变量（也可以不定义）
        global username
        # 传入指定群名进行搜索，之所以搜索，是因为群员的名称信息也在里面
        myroom = itchat.search_chatrooms(name=gname)
        for room in myroom:
            # print(room)
            #遍历所有NickName为键值的信息进行匹配群名
            if room['NickName'] == gname:
                username = room['UserName']
                # 得到群名的唯一标识，进行信息发送
                itchat.send_msg(context, username)
            else:
                print('No groups found')