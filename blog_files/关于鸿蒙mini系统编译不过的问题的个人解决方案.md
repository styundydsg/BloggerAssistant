---
title: 关于鸿蒙mini系统编译不过的问题的个人解决方案
date: 2025-05-23 20:50:03
tags: 
categories: OpenHarmony
---

## 个人总结
wsl ubuntu 22.04  
拉取源码时的命令：repo init -u git@gitee.com:openharmony/manifest.git -b master -g ohos:mini --no-repo-verify  
bash build/prebuilts_download.sh 命令之后会出现一些什么pls check 我的理解就是mini系统不需要，至少我编译成功helloword的时候我没有去管，如果后面需要再去解决。  
还有windows和linux联合的时候vscode远程链接之后vscode打不开那个deveco device tool  
在使用全量的时候也出现了子系统名称不对，忘了解决没有反正后面还有问题就不管了   
忘了忘了  
当时的文档是v5.0.3 Release  
还有如果提示格式错误就检查有没有格式错误，没有删掉那个.build文件


## 配置文件
### ./applications/sample/wifi-iot/app/my_first_app下的BUILD.gn文件
static_library("my_first_app") {
    sources = [
        "hello_world.c"
    ]
    include_dirs = [
        "//utils/native/lite/include"
    ]
}

### build/lite/components/communication.json
    {
      "component": "hello_world_app",
      "description": "hello world samples.",
      "optional": "true",
      "dirs": [
        "applications/sample/wifi-iot/app/my_first_app"
      ],
      "targets": [
        "//applications/sample/wifi-iot/app/my_first_app:my_first_app"
      ],
      "rom": "",
      "ram": "",
      "output": [],
      "adapted_kernel": [ "liteos_m" ],
      "features": [],
      "deps": {
        "components": [],
        "third_party": []
      }
    }

### vendor/hisilicon/hispark_pegasus/config.json
这里我没配置也通过了，下面连接他们说上面那个communication也可以不写，但是我会出错好像是报json的格式错误？去看那个文件也是错误的，那个文件是生成的所以应该找源头
[](https://gitee.com/openharmony/build/issues/I8L7LC?skip_mobile=true)



### \\\wsl$\Ubuntu22.04\root\ohos_master\applications\sample\wifi-iot\app\BUILD.gn

\# Copyright (c) 2020-2022 Huawei Device Co., Ltd.
\# Licensed under the Apache License, Version 2.0 (the "License");
\# you may not use this file except in compliance with the License.
\# You may obtain a copy of the License at
\#
\#     http://www.apache.org/licenses/LICENSE-2.0
\#
\# Unless required by applicable law or agreed to in writing, software
\# distributed under the License is distributed on an "AS IS" BASIS,
\# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
\# See the License for the specific language governing permissions and
\# limitations under the License.

import("//build/lite/config/component/lite_component.gni")

lite_component("app") {
  features = [ "startup","my_first_app" ]
}


### \\\wsl$\Ubuntu22.04\root\ohos_master\applications\sample\wifi-iot\app\my_first_app\BUILD.gn
static_library("my_first_app") {
    sources = [
        "hello_world.c"
    ]
    include_dirs = [
        "//utils/native/lite/include"
    ]
}


### 最后
这些在那个文档都是有配置规则的，不过是在后面，为了写hello world去看也不太可能  
为了写hello world，先是获取源码，买了块移动硬盘发现是qlc就退了，想了想其实100多GB空间还是够的，就强行把五个分区合并成两个了（不是不知道危害，就是突然不想管了就想着前进，五个分区要正常解决要处理太多了，能卸载的卸载，一些文件或工具之类的就直接剪切，想着也没有空间去存那些先移出来的数据（写到这里触发了既视感），最后一些电脑组件损坏了，索引服务启动不了搜索界面出现一大块东西，注册表乱成一团，还好慢慢地恢复到能使用的情况了），然后去寻找减少空间的方法，发现可以只下载mini。按照教程来出现的问题也很多，就又下载small，后来又下载全量，还是很多问题，还有出现不同的问题，最后还是下载mini了，毕竟刚开始小总是好的，确定的东西总是能根据不同的状态出现不同的问题。还有挺多问题已经记不起来了，抱歉。



### 一些链接，希望能有帮助
[轻量编译](https://juejin.cn/post/7430348056199675967)没必要完全按照，太精细反而不太好  
[json格式验证](https://jsonlint.com/)  
[Ubuntu22.04 搭建 OpenHarmony 命令行开发环境](https://blog.csdn.net/qq_36115224/article/details/133966244)  
[[OpenHarmony5.0][环境][教程]OpenHarmony 5.0源码在WSL2 Ubuntu22.04 编译环境搭建教程](https://blog.csdn.net/qq_38844263/article/details/144016387?spm=1001.2014.3001.5506)细  
[一键配置Ubuntu的OpenHarmony基础编译环境](https://blog.csdn.net/wenfei11471/article/details/129922947?spm=1001.2014.3001.5506)23年的  
[关于在Ubuntu中搭建DevEco Device Tool环境出现报错Unable to locate package python-venv](https://developer.huawei.com/consumer/cn/forum/topic/0201103580446197179)  
[如何向OpenHarmony中编译构建自己的子系统、部件和模块](https://blog.csdn.net/weixin_40010764/article/details/140949225)  
这里也很多链接找不到了  