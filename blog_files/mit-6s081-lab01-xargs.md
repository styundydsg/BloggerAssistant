---
title: mit-6s081-lab01-xargs
date: 2025-05-15 15:51:34
tags: mit6.s081_labs
categories: 操作系统
---

#### 前置知识
##### exec
exec命令的基本语法  
exec命令的基本语法如下：  

exec [options] [command] [arguments]

options: 可选参数，用于修改exec的行为。  
command: 要执行的可执行文件或命令。  
arguments: 传递给command的参数。  
如果没有指定command，exec将用于修改当前shell的环境变量、文件描述符等设置。

---

##### read/write 参数012
fd：文件描述符，表示将数据写入到哪里。可以是文件、设备、套接字等。文件描述符是一个整数，通常是由 open 系统调用返回的。  

0：标准输入（stdin）  
1：标准输出（stdout）  
2：标准错误（stderr）  

##### sh < xxx.sh
sh < xargstest.sh 是在 xv6 实验环境中用于测试 xargs 实现的指令，其核心作用是通过输入重定向将脚本内容传递给 sh 解释器执行  
等效于 cat xargstest.sh | sh，但更高效（避免中间管道进程）  
.sh里面可能是一些命令然后重定向给sh执行



#### 代码
```c
#include "kernel/types.h"
#include "user/user.h"
#include "kernel/param.h"

#define MAXLINE 1024

void parse_args(char *line, char **args, int *argc) {
    *argc = 0;
    while (1) {
        // 跳过前导空格
        while (*line == ' ') {
            line++;
        }
        if (*line == '\0') {
            break;
        }
        args[(*argc)++] = line;
        // 寻找参数的结尾
        while (*line != ' ' && *line != '\0') {
            line++;
        }
        // 分割参数
        if (*line == ' ') {
            *line = '\0';
            line++;
        }
        if (*argc >= MAXARG) {
            break;
        }
    }
}

int read_line(int fd, char *buf, int max, int *found_newline) {
    int i = 0;
    *found_newline = 0;
    while (i < max - 1) {
        char ch;
        int n = read(fd, &ch, 1);
        if (n < 0) {
            return -1;
        }
        if (n == 0) {
            break; // EOF
        }
        if (ch == '\n') {
            *found_newline = 1;
            break;
        }
        buf[i++] = ch;
    }
    buf[i] = '\0';
    return i;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        char *msg = "xargs: missing command\n";
        write(2, msg, strlen(msg));
        exit(1);
    }

    while (1) {
        char line[MAXLINE];
        int found_newline;
        int len = read_line(0, line, sizeof(line), &found_newline);
        if (len < 0) {
            char *msg = "xargs: read error\n";
            write(2, msg, strlen(msg));
            exit(1);
        }
        if (len == 0 && !found_newline) {
            break; // EOF
        }

        char *args[MAXARG];
        int new_argc = 0;
        parse_args(line, args, &new_argc);

        char *new_argv[MAXARG];
        int total_args = 0;

        // 添加命令名称
        new_argv[total_args++] = argv[1];

        // 添加原参数
        for (int i = 2; i < argc; i++) {
            if (total_args >= MAXARG) {
                char *msg = "xargs: too many arguments\n";
                write(2, msg, strlen(msg));
                exit(1);
            }
            new_argv[total_args++] = argv[i];
        }

        // 添加新参数
        for (int i = 0; i < new_argc; i++) {
            if (total_args >= MAXARG) {
                char *msg = "xargs: too many arguments\n";
                write(2, msg, strlen(msg));
                exit(1);
            }
            new_argv[total_args++] = args[i];
        }

        new_argv[total_args] = 0; // 参数数组以NULL结尾

        // 创建子进程执行命令
        int pid = fork();
        if (pid < 0) {
            char *msg = "xargs: fork failed\n";
            write(2, msg, strlen(msg));
            exit(1);
        } else if (pid == 0) {
            // 子进程执行命令
            exec(new_argv[0], new_argv);
            // 如果exec失败
            char *msg = "xargs: exec failed\n";
            write(2, msg, strlen(msg));
            exit(1);
        } else {
            // 父进程等待子进程完成
            wait(0);
        }
    }

    exit(0);
}
```


#### 一些解释
**以echo hello too | xargs echo bye为例**
首先会执行echo hello too输出到终端缓冲区，通过管道符传递给xargs的标准输入0  
然后xargs运行时参数为char *argv[]={'xargs','echo','bye'}  
read_line会读取标准输入里的数据也就是hello too到line字符数组  
parse_args解析line存到args指针数组里  
此时args里就是{"hello\0","too\0"}  
构造一个新的命令new_argv  
这个新命令的索引：  
0:echo  
1:bye   
添加args  
2:hello  
3:too  
4:0
最后exec执行输出bye hello too，中间的空格应该是自己识别的吧


#### 整理一下AI的总结
在Linux系统中，管道符|通过以下机制将数据从左侧命令传递给右侧命令，具体流程如下：  
一、管道符的底层实现原理  
匿名管道创建  
当用户执行cmd1 | cmd2时，Shell会调用pipe()系统调用创建一个匿名管道（Anonymous Pipe），该管道由两个文件描述符（read_fd和write_fd）表示。  
进程间文件描述符重定向  
Shell通过fork()创建两个子进程（分别执行cmd1和cmd2），并利用dup2()将文件描述符重定向：  
cmd1的标准输出（文件描述符1）被重定向到管道的write_fd，其输出不再直接发送到终端，而是写入管道。  
cmd2的标准输入（文件描述符0）被重定向到管道的read_fd，其输入源变为管道。  
内核缓冲区的数据传输  
左侧命令（cmd1）的输出数据首先写入内核空间的管道缓冲区（默认4KB），而非直接发送到屏幕。  
右侧命令（cmd2）通过read()系统调用从管道缓冲区按需读取数据，若缓冲区为空则阻塞等待。  

管道是单向通信，数据从echo的stdout流向cat的stdin。

存储位置：当直接执行echo hello时，字符串hello默认通过标准输出（文件描述符1）发送到终端屏幕（即字符设备文件，如/dev/tty） echo内部应该有一个print 从0转变为1
