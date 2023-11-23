import datetime
import json
import requests


def read_config():
    with open("config.json", mode="r", encoding="utf-8") as f:
        return json.loads(f.read())


config = read_config()


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


def notify(msg):
    try:
        requests.post(
            url="https://notify-api.line.me/api/notify",
            headers={"Authorization": "Bearer " + config["LINE_TOKEN"]},
            data={"message": msg},
            timeout=30,
        )
    except Exception:
        ...
