import redis

try:
    r = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True,password='123456')
    # PING 命令用于测试连接
    if r.ping():
        print("成功连接到 Redis!")
    else:
        print("连接 Redis 失败。")
except redis.exceptions.ConnectionError as e:
    print(f"无法连接到 Redis: {e}")

