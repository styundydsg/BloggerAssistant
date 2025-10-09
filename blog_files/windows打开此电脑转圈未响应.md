---
title: windows打开此电脑转圈未响应
date: 2025-06-07 16:25:51
tags: 解决方案
categories: 解决方案
---

问题原因：
我使用虚拟机的nfs作为服务端，然后windows作为客户端挂载，然后没有卸载

所以使用     net use X: /delete   进行删除 就可以了

     