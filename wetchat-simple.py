#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itchat.content import *
import winsound
import itchat
import time
import sys
from multiprocessing import Lock

from collections import deque
from datetime import datetime, timedelta
from time import sleep
import thread

ToReply = []
ReplyNow = []
L = Lock()


@itchat.msg_register([TEXT, PICTURE, RECORDING, SHARING])
def auto_msg(msg):
    if not ReplyNow:
        ReplyNow.append(msg.user)
    else:
        ReplyNow[0] = msg.user
    if msg.user.RemarkName not in ToReply:
        ToReply.append(msg.user.RemarkName)
    winsound.MessageBeep(winsound.MB_ICONHAND)
    L.acquire()
    if msg.type == 'Text':
        print msg.user.RemarkName + '[' + datetime.now().strftime("%H:%M") + ']:', msg.text
    else:
        print msg.user.RemarkName + '[' + datetime.now().strftime("%H:%M") + ']:', '('+msg.type+')'
    L.release()
    # msgQ.append((msg.user, datetime.now(), msg.text))


def replymsg():
    while True:
        cmd = raw_input().decode(sys.stdin.encoding)
        if cmd == u'l':
            i = 0
            for name in ToReply:
                print '[' + str(i) + ']' + name,
                i = i + 1
            print ""

        elif cmd == u's':
            if ReplyNow:
                tosend = ReplyNow.pop()
                name = tosend.RemarkName
                L.acquire()
                msg = raw_input(u"发给" + name + ': ').decode(sys.stdin.encoding)
                L.release()
                if msg != u'q':
                    tosend.send(msg)
                    print '(' + msg + ')', "->", name
                else:
                    print "->", name
        elif u'0' <= cmd <= u'9':
            if ToReply:
                try:
                    index = int(cmd)
                    if index < len(ToReply):
                        name = ToReply[index]
                        reply = itchat.search_friends(remarkName=name)
                        L.acquire()
                        msg = raw_input(u"发给" + name + ': ').decode(sys.stdin.encoding)
                        L.release()
                        if msg != u'q':
                            reply[0].send(msg)
                            print '(' + msg + ')', "->", name
                        else:
                            print "->", name
                except:
                    print 'OFR'  # out of range
        else:
            print "unknow cmd"

        sleep(1)


itchat.auto_login()
thread.start_new_thread(replymsg, ())
itchat.run()
