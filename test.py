import json
from tools import prikey2pubkey, pubkey2addr, wif2prikey


def test():
    with open("cases.json", "r", encoding="utf-8") as f:
        tbl = json.loads(f.read())

    for t in tbl:
        prikey = wif2prikey(t["wif"])
        pubkey = prikey2pubkey(prikey)
        assert pubkey == t["pubkey"]
        addr = pubkey2addr(pubkey, testnet=False)
        assert addr == t["addr"]

    print("done")


test()
