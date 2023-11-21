import datetime
from tqdm import tqdm


def with_timer(*arg_wrapper, **kwargs_wrapper):
    def _with_timer(func):
        def wrapper(*args, **kwargs):
            time_start = datetime.datetime.now()
            rtn = func(*args, **kwargs)
            time_end = datetime.datetime.now()

            delta = (time_end - time_start)

            print(kwargs_wrapper["template"].format(time=f"{delta}"))

            return rtn
        return wrapper
    return _with_timer


def func(i):
    # print(i)
    ...


def gen(arg):
    for g in range(arg):
        yield g


@with_timer(template="Delta: {time} (s)")
def run():
    arg = 2**28
    # rng = range(arg)
    rng = gen(arg)

    for i in tqdm(rng, total=arg):
        func(i)


run()
