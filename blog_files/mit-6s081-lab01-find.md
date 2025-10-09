---
title: mit_6s081_lab01_find
date: 2025-05-13 11:22:32
tags: mit6.s081_labs
categories: 操作系统
---

##### 知识点：
1. 
    stat 命令用于显示文件或文件系统状态的详细信息。它提供了比 ls -l 更加详细的输出，包括时间戳、权限、所有者等信息。
    用法：stat [选项]... 文件...
    显示文件或文件系统的状态。

---
2. 
    ‌dirent‌是C语言中用于文件操作的一个头文件，主要提供目录遍历功能，适用于需要访问文件系统的程序。在Linux等Unix-like系统中，它是标准库的一部分，但在Windows系统中需要使用其他API。dirent通过struct dirent结构体和一系列函数，如opendir(), readdir(), 和closedir()等，提供了基本的目录操作接口。

    dirent结构体
    dirent结构体用于描述目录中的条目，主要成员包括：

    ‌d_ino‌：文件的inode号码。
    ‌d_reclen‌：目录项的长度（以字节为单位）。
    ‌d_namlen‌：目录项名称的长度（不包括终止null字符）。
    ‌d_name‌：目录项的名称（以null结尾的字符串）。
    主要函数
    ‌opendir()‌：打开一个目录流，返回一个指向DIR结构的指针。如果无法打开目录，返回NULL。
    ‌readdir()‌：从目录流中读取下一个目录项，返回一个指向dirent结构体的指针。如果目录流中没有更多目录项，返回NULL。
    ‌closedir()‌：关闭一个目录流，释放与该目录流关联的系统资源。
    ‌rewinddir()‌：将目录流重置到开头。
    ‌seekdir()‌：将目录流移动到指定位置。
    ‌telldir()‌：返回目录流的当前位置。
    <!-- more -->

---
3. 
    ‌Linux的open函数的参数包括‌：

    ‌pathname‌：这是要打开或创建的文件的路径名，可以是绝对路径或相对路径。

    ‌flags‌：用于指定文件的打开方式，包括以下常见标志：

    ‌O_RDONLY‌：以只读模式打开文件。
    ‌O_WRONLY‌：以只写模式打开文件。
    ‌O_RDWR‌：以读写模式打开文件。
    ‌O_CREAT‌：如果文件不存在，则创建该文件。
    ‌O_EXCL‌：与O_CREAT一起使用时，如果文件已存在，则返回错误。
    ‌O_TRUNC‌：如果文件已存在，则将其长度截断为0。
    ‌O_APPEND‌：以追加方式打开文件。
    ‌O_NONBLOCK‌：以非阻塞模式打开文件。
    ‌O_SYNC‌：每次写操作后都进行同步。
    ‌O_RSYNC‌：读操作等待所有写操作完成后再进行。

---
4. 
    在C语言编程中，struct dirent 和 struct stat 是两个常用的结构体，主要用于文件和目录操作。以下是对这两个结构体的详细解释：
    a.
    struct dirent
    struct dirent 是在 <dirent.h> 头文件中定义的，用于表示目录中的一个条目（即文件或子目录）。它通常用于目录遍历。
    成员解释
    ino_t d_ino：文件的inode号码。
    off_t d_off：目录文件开头到本条目的偏移。
    unsigned short d_reclen：当前条目的长度。
    unsigned char d_type：文件类型（仅在某些系统中支持，如Linux 2.6及以上版本）。
    char d_name[]：文件名。
    示例代码
    ```c
    #include <stdio.h>
    #include <dirent.h>
    int main() {
        DIR *dir;
        struct dirent *de;
        dir = opendir("."); // 打开当前目录
        if (dir == NULL) {
            perror("opendir");
            return 1;
        }
        while ((de = readdir(dir)) != NULL) {
            printf("File: %s\n", de->d_name);
        }
        closedir(dir);
        return 0;
    }
    ```
    b.
    struct stat
    struct stat 是在 <sys/stat.h> 头文件中定义的，用于表示文件的状态信息。它包含文件的详细信息，如大小、权限、所有者等。
    成员解释
    dev_t st_dev：文件所在设备的ID。
    ino_t st_ino：文件的inode号码。
    mode_t st_mode：文件的类型和权限。
    nlink_t st_nlink：文件的硬链接数。
    uid_t st_uid：文件所有者的用户ID。
    gid_t st_gid：文件所有者的组ID。
    dev_t st_rdev：若文件为设备文件，此字段为设备类型。
    off_t st_size：文件大小（字节数）。
    blksize_t st_blksize：文件系统的块大小。
    blkcnt_t st_blocks：文件占用的块数。
    struct timespec st_atim：最后一次访问时间。
    struct timespec st_mtim：最后一次修改时间。
    struct timespec st_ctim：最后一次状态改变时间。
    示例代码
    ```c
    #include <stdio.h>
    #include <sys/stat.h>
    #include <unistd.h>
    int main() {
        struct stat st;
        if (stat("example.txt", &st) == -1) {
            perror("stat");
            return 1;
        }
        printf("File size: %ld bytes\n", st.st_size);
        printf("Last modified time: %ld\n", st.st_mtime);
        return 0;
    }
    ```

---
5. 
    fstat() 是一个系统调用，用于获取打开文件的状态信息。它与 stat() 类似，但 fstat() 接受一个文件描述符作为参数，而不是文件路径。这在处理已经打开的文件时非常有用。
    函数原型
    int fstat(int fd, struct stat *st);
    参数解释
    int fd：文件描述符，它是通过 open(), creat(), dup(), fcntl(), socket(), accept(), 等系统调用获得的。
    struct stat *st：指向 struct stat 结构体的指针，用于存储文件的状态信息。
    返回值
    成功：返回 0。
    失败：返回 -1，并设置 errno 以指示错误。
    struct stat 结构体
    struct stat 结构体包含了许多关于文件的详细信息，如：
    st_size：文件的大小（字节）。
    st_mode：文件类型和权限。
    st_uid：文件所有者的用户ID。
    st_gid：文件所有者的组ID。
    st_atime：最后访问时间。
    st_mtime：最后修改时间。
    st_ctime：文件状态改变时间。
    等等。
    示例代码
    以下是一个使用 fstat() 的简单示例，它打开一个文件，并获取其大小：
    ```c
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    int main() {
        int fd;
        struct stat st;
        // 打开文件
        fd = open("example.txt", O_RDONLY);
        if (fd == -1) {
            perror("open");
            return EXIT_FAILURE;
        }
        // 获取文件状态信息
        if (fstat(fd, &st) == -1) {
            perror("fstat");
            close(fd);
            return EXIT_FAILURE;
        }
        // 打印文件大小
        printf("File size: %ld bytes\n", st.st_size);
        // 关闭文件
        close(fd);
        return EXIT_SUCCESS;
    }
    ```
    注意事项
    使用 fstat() 前，确保文件描述符是有效的。
    在使用完文件后，应关闭文件描述符以释放资源。

---
6. 
    fprintf是C/C++中的一个格式化库函数，位于头文件<cstdio>;中，其作用是格式化输出到一个流文件中；函数原型为int fprintf( FILE *stream, const char *format, [ argument ]...)，fprintf()函数根据指定的格式(format)，向输出流(stream)写入数据(argument)。

---
7. 
    echo > b
    命令解释：
    echo：用于在终端输出文本或字符串。
    \>：重定向符号，将输出写入到指定的文件中。如果文件不存在，则会创建该文件；如果文件已存在，则覆盖其内容。
    b：文件名。
    作用：
    创建一个名为 b 的空文件。因为 echo 后面没有跟任何字符串，所以 b 文件的内容为空。

---
8. 
    在XV6操作系统中，DIRSIZ 是一个宏定义，表示目录条目（struct dirent）中文件名的最大长度。它的值通常是14字节（定义在 kernel/fs.h 中），这是XV6文件系统的设计限制。

    DIRSIZ 的作用
    目录条目结构：在XV6中，目录由一系列目录条目（struct dirent）组成，每个条目包含：

    inum：文件的inode编号（2字节）

    name：文件名（DIRSIZ 字节，通常是14字节）

    文件名存储：DIRSIZ 限制了文件名的最大长度（例如，"a.txt" 可以，但 "very_long_filename.txt" 可能被截断）

---
9. 
    void *memmove( void* dest, const void* src, size_t count );

---
##### 代码实例：
```c
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#include "kernel/fs.h"

// 从路径中提取文件名
char*
get_filename(char *path)
{
    char *p;
    // 从后往前找到最后一个斜杠
    for(p = path + strlen(path); p >= path && *p != '/'; p--);
    p++;
    return p;
}

void
find(char *path, char *target)
{
    char buf[512], *p;
    int fd;
    struct dirent de;
    struct stat st;

    if((fd = open(path, 0)) < 0){
        fprintf(2, "find: cannot open %s\n", path);
        return;
    }
    
    if(fstat(fd, &st) < 0){
        fprintf(2, "find: cannot stat %s\n", path);
        close(fd);
        return;
    }

    switch(st.type){
    case T_FILE:
        // 比较文件名部分
        if(strcmp(get_filename(path), target) == 0)
            printf("%s\n", path);
        break;

    case T_DIR:
        if(strlen(path) + 1 + DIRSIZ + 1 > sizeof buf){
            printf("find: path too long\n");
            break;
        }
        strcpy(buf, path);
        p = buf + strlen(buf);
        *p++ = '/'; // 添加斜杠
        while(read(fd, &de, sizeof(de)) == sizeof(de)){
            if(de.inum == 0)
                continue;
            memmove(p, de.name, DIRSIZ);
            p[DIRSIZ] = 0; // 确保字符串终止
            // 跳过.和..
            if(!strcmp(de.name, ".") || !strcmp(de.name, ".."))
                continue;
            find(buf, target); // 递归处理子目录
        }
        break;
    }
    close(fd);                                                                                                     
}    

int
main(int argc, char *argv[])
{
    if(argc != 3){
        fprintf(2, "Usage: find <directory> <filename>\n");
        exit(1);
    }
    find(argv[1], argv[2]);
    exit(0);
}
```