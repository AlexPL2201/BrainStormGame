if __name__ == '__main__':
    import redis

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
