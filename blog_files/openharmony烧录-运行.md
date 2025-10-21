---
title: openharmony烧录/运行
date: 2025-05-27 19:33:07
tags: 
categories: OpenHarmony
---
### 关键语句
*   **启动与加载失败**
    `ready to load at 0x10a000 ccccccccccload fail 0xc35a69a6 ready`
    `Wait SELoadr ACK overtime Wait connect success flag (hisilicon) overtime.`
*   **AT指令无返回**
### 烧录问题
*   **HiBurn 工具**
    烧录时使用 `OHOS_Image.bin` 文件。文档中可能提到选择两个文件，但实际应选择一个整合好的文件，这可能是文档的疏漏。
### AT指令问题
*   **运行环境**
    AT指令需在特定工具（如 IPOP）下运行。
*   **发送格式**
    发送AT指令后必须加回车，否则可能无反应。不同串口调试助手的处理方式可能不同。

