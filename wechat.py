#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itchat
import time
import sys
import re
from collections import deque
from datetime import datetime,timedelta
from time import sleep
import thread
msgQ = deque([])
Names = [u'嘴里含木',u'困']  # add your friends' nickname or remarkname here
sendlist = []
def input(msgQ):
    try:
        msgQ.append(raw_input(u"我: ").decode(sys.stdin.encoding))
    except:
        msgQ.append(u"有事不在(自动回复)")


@itchat.msg_register(itchat.content.TEXT)
def auto_msg(msg):
    msgQ.append((msg.user, datetime.now(), msg.text))

    

Pattern1 = re.compile(u"^([0-9]+)$")
Pattern2 = re.compile(u"([0-9]+)个?(小时|h|min|m|分钟)([0-9]*).*后(叫|提醒|让|说)(.*)")
#group                     0            1                2            3          4
Pattern3 = re.compile(u"([明|今]?)天?([早|晚]?)上?([0-9]{1,2})([点|分]?)([0-9]{0,2})(半?).*(叫|提醒|让|说)(.*)")
#grooup                      0          1             2          3          4       5         6          7
        
def ParseMsg(verb,msg):
    res = msg
    if verb in u'叫提醒让':
        if msg[0] == u'我':
             res = msg[1:]
    else:   #说
        if u'爱' in msg or u'喜欢' in msg or  u'想' in msg:    #可能有调情的话
            return msg + u',么么哒'
    if not res:
        res = u'到时间了'
    return res + u'(自动)'

    
def ParseCMD(timestamp,msg):    
    rtime = timestamp       #由解析消息得到的最终时间
    todo = u''
    if Pattern1.match(msg): 
        rtime = rtime.replace(minute=int(Pattern1.match(msg).group(1)),second=0)
        todo = ParseMsg(u'叫',u'')
    elif Pattern2.match(msg):
        t = Pattern2.match(msg).groups()
        todo = ParseMsg(t[3],t[4])
        if t[1] in [u'小时',u'h']:
            rtime = rtime + timedelta(hours=int(t[0]))
            if t[2]:
                rtime = rtime + timedelta(minutes=int(t[2]))
        else:  #eg:40分钟后叫我
            rtime = rtime + timedelta(minutes=int(t[0]))
    elif Pattern3.match(msg):
        rtime = rtime.replace(second=0)   #秒位清零
        t = Pattern3.match(msg).groups()
        todo = ParseMsg(t[6],t[7])
        if t[3] == u'分':     #eg: 40分叫我
            rtime = rtime.replace(minute=int(t[2]))
        elif t[3] == u'点':
            hour = int(t[2])
            minute = 0
            if t[0] == u'明':
                rtime = rtime + timedelta(days=1)  #日期上加一天
            if t[4]:
                minute = int(t[4])
            elif t[5]:
                minute = 30
            else:
                minute = 0
               
            if t[1] == u'晚'and hour <= 12:
                hour += 12
            rtime = rtime.replace(hour=hour,minute=minute)
            if rtime < timestamp:   #eg: 我在晚上的时候,说12点半叫我回宿舍
                rtime = rtime + timedelta(hours=12) 
        else:
            rtime = rtime.replace(minute=int(t[2])) #eg:40叫我          
    else:
        return None
    
    return rtime,todo

    
    
def HandleMsg():
    while True:
        if bool(msgQ):
            msg = msgQ.popleft()
            for name in Names:
                if msg[0].RemarkName == name or msg[0].NickName == name or msg[0].UserName == name:
                    try:
                        res = ParseCMD(msg[1],msg[2])
                        if res:
                            sendlist.append((res,msg[0]))
                            if u'爱' in msg[2]:
                                msg[0].send(u"嗯")
                            else:
                                msg[0].send(u"好的(机器人)")
                            print "insert","time=",res[0].ctime(),res[1]
                    except:
                        print 'error'
            if msg[0].RemarkName:
                name = msg[0].RemarkName    #优先打印备注名字
            else:
                name = msg[0].NickName
            print name+'['+msg[1].strftime("%m-%d %H:%M")+']:',msg[2]
        else:
            sleep(1)

def SendMsg():
    while True:
        if bool(sendlist):
            for i in sendlist:
                if datetime.now() >= i[0][0]:
                    print "send"
                    i[1].send(i[0][1])
                    sendlist.remove(i)
        sleep(1)

        
                        
if __name__ == '__main__':                                       
    thread.start_new_thread(HandleMsg,())
    thread.start_new_thread(SendMsg,())
    itchat.auto_login()
    itchat.run()
