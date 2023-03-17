from functools import wraps
from multiprocessing import Process, Value
from time import sleep


class RateLimitExceeded(Exception):
    ...


class SlowDownException(Exception):
    ...


class RateLimiter:
    def __init__(self, limit, period: int):
        """

        :param limit: access limit
        :param period: period in seconds
        """
        self.watchman = None
        self.current_num = Value('i', 0)
        self.limit = limit
        self.period = period

    def start(self):
        self.watchman = Process(target=self.watch)
        self.watchman.start()

    def add(self):
        with self.current_num.get_lock():
            if self.current_num.value < self.limit:
                self.current_num.value += 1
            else:
                raise RateLimitExceeded

    def end(self):
        self.watchman.terminate()

    def watch(self):
        while True:
            sleep(self.period)
            self.current_num.value = 0


def rate_limit(func):
    rate_limit.limiter = RateLimiter(10, 15)
    rate_limit.limiter.start()

    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 100
        while retries != 0:
            try:
                rate_limit.limiter.add()
            except RateLimitExceeded:
                sleep(2)
                retries -= 1
            else:
                return func(*args, **kwargs)
    return wrapper
