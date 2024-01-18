import sys; sys.path.append(".")    # noqa
import pyattacker


def test():
    print("targets")

    for file in [
        pyattacker.bip39,
        pyattacker.tools,
    ]:
        print("-",file.__name__)
        file.test()
    
    print("\nsuccess")


test()
