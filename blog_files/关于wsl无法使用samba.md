---
title: 关于wsl无法使用samba
date: 2025-05-17 19:23:52
tags: wsl
categories: 
    - linux
---

问题：WSL 默认不支持直接运行 smbd  
原因：  
smbd 需要访问低层网络功能（如绑定到端口 445），WSL2 虚拟环境不允许这样做。  

WSL2 的网络和 Windows 是隔离的（类似虚拟机），而且端口 445 通常已被 Windows 自身的 SMB 服务占用，smbd 无法监听。  

推荐解决方案：用 Windows 的 SMB 服务共享 WSL 文件夹

方法：  
1. wsl -l -v  
输出：NAME      STATE           VERSION  
Ubuntu    Running         2  
记住这个name  
2. 在资源管理器地址栏输入\\wsl$\name\home\share   \home\share是共享的文件夹自行寻找，此时可以验证在wsl里共享文件夹下创建一个文件在windows看有没有
