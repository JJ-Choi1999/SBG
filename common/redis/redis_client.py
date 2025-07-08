import redis
from redis.typing import KeyT


class RedisClient:

    def __init__(self, host='localhost', port=6379, db=0, **connection_kwargs):
        # 使用连接池（推荐高并发场景）
        self.__pool = redis.ConnectionPool(host=host, port=port, db=db, **connection_kwargs)
        self.__r = redis.Redis(connection_pool=self.__pool)

    @property
    def instances(self):
        return self.__r

    def save_str(self, key: str, value: any, time: int | None = None) -> bool:
        # 返回是否保存成功
        save_result = self.__r.set(name=key, value=value, ex=time)
        if time: self.__r.expire(key, time=time)
        return save_result

    def save_hash(self, key: str, hash_map: dict, time: int | None = None) -> int:
        # 返回新增的key数目
        save_result = self.__r.hset(name=key, mapping=hash_map)
        if time: self.__r.expire(key, time=time)
        return save_result

    def save_list(self, key: str, list_data: list, time: int | None = None) -> int:
        # 全量更新, 返回右侧插入值长度
        if self.exists(key): self.delete(key)
        list_result = self.__r.rpush(key, *list_data)
        if time: self.__r.expire(key, time=time)
        return list_result

    def save_set(self, key: str, set_data: set, time: int | None = None) -> int:
        # 全量更新, 返回插入set长度
        if self.exists(key): self.delete(key)
        set_result = self.__r.sadd(key, *set_data)
        if time: self.__r.expire(key, time=time)
        return set_result

    def save_sorted_set(self, key: str, sorted_set_data: dict, time: int | None = None) -> int:
        # 全量更新, 插入 sorted_set 长度
        if self.exists(key): self.delete(key)
        ss_result = self.__r.zadd(key, sorted_set_data)
        if time: self.__r.expire(key, time=time)
        return ss_result

    def read_str(self, keys: list[str], type_trans_func: any = None) -> list[bytes] | list[any]:

        # 默认提取出来的值是 bytes 列表
        vals = self.__r.mget(keys)

        if type_trans_func:
            new_vals = []
            for val in vals:
                if not val: continue
                new_vals.append(type_trans_func(val))
            return new_vals

        return vals

    def read_hash(self, keys: list[str], type_trans_func: any = None) -> list[dict[bytes, bytes]] | list[dict]:
        hash_results = []
        for key in keys:
            hget_result = self.__r.hgetall(key)
            if type_trans_func: hget_result = type_trans_func(hget_result)
            hash_results.append(hget_result)

        return hash_results

    def read_list(self, keys: list[str], type_trans_func: any = None) -> list[list[bytes]] | list[list[any]]:
        list_results = []
        for key in keys:
            lrange_result = self.__r.lrange(key, 0, -1)
            if type_trans_func: lrange_result = type_trans_func(lrange_result)
            list_results.append(lrange_result)

        return list_results

    def read_set(self, keys: list[str], type_trans_func: any = None) -> list[set[bytes]] | list[set[any]]:
        set_results = []
        for key in keys:
            smembers_result = self.__r.smembers(key)
            if type_trans_func: smembers_result = type_trans_func(smembers_result)
            set_results.append(smembers_result)

        return set_results

    def read_sorted_set(self, keys: list[str], type_trans_func: any = None) -> list[list[bytes]] | list[list[any]]:
        ss_results = []
        for key in keys:
            zrange_result = self.__r.zrange(key, 0, -1)
            if type_trans_func: zrange_result = type_trans_func(zrange_result)
            ss_results.append(zrange_result)

        return ss_results

    def delete(self, *keys: KeyT) -> int:
        # 返回成功删除的key数目
        return self.__r.delete(*keys)

    def exists(self, key: str) -> bool:
        return self.__r.exists(key)

    def close(self):
        self.__r.close()

if __name__ == '__main__':
    redis_client = RedisClient()
    r = redis_client.instances

    # set_result = redis_client.save_set('myset', {'a', 'b', 'c'}, 100)
    # print(f'set_result:', set_result)
    # set_result = redis_client.save_set('myset', {'a', 'b'}, 100)
    # print(f'set_result:', set_result)
    # set_results = redis_client.read_set(['myset'])
    # print(f'set_results:', set_results)

    # 添加元素并指定分数
    ss_result = redis_client.save_sorted_set('sorted_set', {'a': 1, 'b': 2, 'c': 3}, 100)
    print("ss_result:", ss_result)
    # 按分数范围获取元素
    members = redis_client.read_sorted_set(['sorted_set'])
    print(f'members:', members)