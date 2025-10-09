---
title: mit-6s081-lab02-sysinfo
date: 2025-06-06 11:04:31
tags: mit6.s081_labs
categories: 操作系统
---
像之前那样添加syscall，和$U/_sysinfotest

### 代码
kernel/syscall.h
```c
#define SYS_sysinfo 23
```
kernel/syscall.c
```c
extern uint64 sys_sysinfo(void);

[SYS_sysinfo] sys_sysinfo
```

kernel/sysproc.c
```c
#include "sysinfo.h"

int sys_sysinfo(void) {
    struct sysinfo info;
    uint64 addr;
    struct proc *p = myproc();

    if (argaddr(0, &addr) < 0)
        return -1;

    info.freemem = kfreemem();
    info.nproc = nproc();

    if (copyout(p->pagetable, addr, (char *)&info, sizeof(info)) < 0)
        return -1;

    return 0;
}
```

kernel/kalloc.c
```c
void *
kalloc(void)
{
  struct run *r;

  acquire(&kmem.lock);
  r = kmem.freelist;
  if(r)
    kmem.freelist = r->next;
  release(&kmem.lock);

  if(r)
    memset((char*)r, 5, PGSIZE); // fill with junk
  return (void*)r;
}
```


```c
uint64
kfreemem(void)
{
struct run *r;
uint64 pages=0;
acquire(&kmem.lock);
for(r=kmem.freelist;r;r=r->next)
        pages++;
release(&kmem.lock);

return pages*PGSIZE;
}
```


kernel/proc.c
```c
int
nproc(void)
{
        int count=0;
        struct proc* p;
        acquire(&pid_lock);
        acquire(&wait_lock);
        for(p=proc;p<&proc[NPROC];p++)
        {
                if(p->state!=UNUSED){
                        count++;
                }

        }
        release(&wait_lock);
        release(&pid_lock);

        return count;
}
```

然后输入sysinfotest

