import src


def test():
    for file in [
        src.bip39,
        src.tools,
    ]:
        file.test()


test()
