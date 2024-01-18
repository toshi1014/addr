import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


URL_BASE = "https://etherscan.io/accounts/{page}?ps={rows}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}
TIMEOUT = 10
DOM_ADDR = ("a", {"class": "me-1"})
IGNORE = {"0x71c7656ec7ab88b098defb751b7401b5f6d8976f"}


def get_html(url):
    res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if res.status_code == 200:
        return res.text
    else:
        raise Exception("bad response")


def extract_address(html):
    soup = BeautifulSoup(html, "html.parser")
    return {
        a_tag.get("href").split("/")[-1]
        for a_tag in soup.find_all(*DOM_ADDR)
    } - IGNORE


def get_eth_address():
    addr_list = []

    for page in tqdm(range(100)):
        addr_list += extract_address(
            get_html(url=URL_BASE.format(page=page+1, rows=100))
        )
        time.sleep(0.2)

    df = pd.DataFrame({"address": addr_list})
    df.to_csv("addr_list.eth.tsv", sep="\t", index=False)
    return addr_list


get_eth_address()
