import redis

r = redis.Redis(db=0)

elements = r.zrange("players", 0, -1)

print(elements)