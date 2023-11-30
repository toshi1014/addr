import sys
sys.path.append(".")    # noqa
from src import pyattacker


def test():
    for file in [
        pyattacker.bip39,
        pyattacker.tools,
    ]:
        file.test()


test()
