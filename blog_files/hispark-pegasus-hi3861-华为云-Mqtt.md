---
title: hispark_pegasus/hi3861/华为云/Mqtt
date: 2025-08-05 19:23:01
tags: 
---
需要的条件

clientid
user
pwd

接入信息找mqtt接入的域名，ping域名得到地址，端口选择1833
topic在topic管理那里查找消息上报或者属性上报
选择消息上报的话可以根据得到的消息继续通过规则转发到设备
然后根据使用的库进行连接就行了

在规则引擎配置的时候设置的topic
在设备端比如pc可以用接入信息的ip+端口+这个topic去订阅

