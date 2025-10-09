---
title: mit_6s081_lab01_primes
date: 2025-05-12 20:01:34
tags: mit6.s081_labs
categories: 操作系统
---

这是关于mit6.s081课程中的lab01中primes实现的记录


<!-- more -->

##### 代码实现：
```c
    #include "kernel/types.h"
    #include "user/user.h"  // 使用xv6原生声明

    // 修改后的正确实现
    void itoa(int num, char* buf) {
        int i = 0;
        if (num == 0) {
            buf[i++] = '0';
        } else {
            int start = i;
            while (num > 0) {
                buf[i++] = (num % 10) + '0';
                num /= 10;
            }
            // 反转数字部分
            for (int j = start; j < (i + start)/2; j++) {
                char tmp = buf[j];
                buf[j] = buf[i + start - j - 1];
                buf[i + start - j - 1] = tmp;
            }
        }
        buf[i] = '\0';
    }

    void sieve(int read_fd) {
        int prime;
        if (read(read_fd, &prime, sizeof(prime)) <= 0) {
            close(read_fd);
            exit(0);
        }

        // 构建输出信息（完全使用xv6兼容方式）
        char buf[32];
        char *p = buf;
        memmove(p, "prime ", 6);
        p += 6;
        itoa(prime, p);
        while (*p) p++;
        *p++ = '\n';

        write(1, buf, p - buf);

        int fd[2];
        pipe(fd);

        if (fork() == 0) {
            close(fd[1]);
            sieve(fd[0]);
            exit(0);
        } else {
            close(fd[0]);
            int num;
        while (read(read_fd, &num, sizeof(num)) > 0) {
                if (num % prime != 0) {
                    write(fd[1], &num, sizeof(num));
                }
            }
            close(fd[1]);
            close(read_fd);
            wait(0);
            exit(0);
        }
    }

    int main() {
        int fd[2];
        pipe(fd);

        for (int i = 2; i <= 35; i++) {
            write(fd[1], &i, sizeof(i));
        }
        close(fd[1]);

        sieve(fd[0]);
        close(fd[0]);

        exit(0);

    }
```

---

##### 注意事项：
1. 在UPROGS中添加的文件primes.c前面需要有下划线，不然会有未定义问题

---

##### AI总结：
1. 当我们执行 make qemu 时，实际上是在执行 Makefile 中定义的 qemu 目标
   &nbsp;
2. 
    假设我们有以下 Makefile 内容：
    ```
    QEMU = qemu-system-i386 
    QEMUOPTS = -drive file=$(OBJDIR)/kern/kernel.img,index=0,media=disk,format=raw -serial mon:stdio -gdb tcp::$(GDBPORT)
    OBJDIR = build

    qemu: $(OBJDIR)/kern/kernel.img
        $(QEMU)$(QEMUOPTS)
    ```

    执行 make qemu 时，会先检查 build/kern/kernel.img 是否存在，然后运行：

    ```
    qemu-system-i386 -drive file=build/kern/kernel.img,index=0,media=disk,format=raw -serial mon:stdio -gdb tcp::$(GDBPORT)
    ```

    -drive file=...,index=...,media=...,format=...：指定虚拟硬盘的文件、索引、媒体类型和格式。
    -serial mon:stdio：将串行端口输出到标准输入输出。
    -gdb tcp::\$(GDBPORT)：启用 GDB 调试服务，监听指定的端口。
    &nbsp;
3. vim全选删除：ggdG
   查找替换: :%s原/目标/g  g是全局
   查找: /<查找字符串> 
   find用法: find .（当前目录） -name <？>
   &nbsp;
4. 在Unix-like系统（包括xv6）中，write(1, buf, p - buf) 中的 1 是标准输出（stdout）的文件描述符。以下是详细解释：

    文件描述符（File Descriptor）的含义
    在Unix系统中，所有输入/输出资源（文件、管道、设备等）都被抽象为文件描述符。每个进程启动时会默认打开三个文件描述符：

    0：标准输入（stdin，键盘输入）

    1：标准输出（stdout，屏幕输出）

    2：标准错误（stderr，错误信息输出）
    &nbsp;
    write(1, buf, p - buf);
    参数1：表示要向标准输出（屏幕/终端）写入数据。
 
    参数2：要写入的数据缓冲区（buf）。

    参数3：要写入的字节数（p - buf 计算缓冲区长度）。

    这行代码的作用是：将 buf 中从起始位置到 p 指针之间的内容输出到屏幕上。
    &nbsp;
5. 是的，通常情况下，调用一次read方法就读取一个数据。通常情况下，当你从管道中读取数据时，一旦数据被读取，它就会从管道中消失。管道（pipe）是一种用于进程间通信的机制，它允许一个进程（写入端）将数据发送到另一个进程（读取端）。
   &nbsp;
6. 在Unix-like系统中，文件描述符（file descriptor）是一个非负整数，它用于唯一标识一个打开的文件或资源。文件描述符是由操作系统内核管理的，它们与文件、管道、套接字等资源相关联。当你定义一个数组来充当文件描述符时，你实际上是在模拟文件描述符的行为。这不是真正的文件描述符，而是一种编程技巧，用于在用户空间中管理多个文件或资源。


##### 课程链接
[Lab: Xv6 and Unix utilities](https://pdos.csail.mit.edu/6.828/2021/labs/util.html )

   



   



