from requests_html import HTMLSession
from typing import List
from time import sleep
import pandas as pd
from numpy import nan
import pickle
from logging import getLogger, StreamHandler, Formatter, DEBUG
logger = getLogger(__name__)
logger.setLevel(DEBUG)
ch = StreamHandler()
ch.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


def get_articles(base_domain: str, kind: str) -> List[str]:
    base_url = base_domain + kind
    session = HTMLSession()
    r = session.get(base_url + ".html")
    all_articles = pd.Series(list(r.html.links), name=kind)
    articles = all_articles[all_articles.str.startswith("20")]
    logger.debug("Checked: %s", base_url)
    sleep(10)
    r = session.get(base_url + "_list.html")
    all_art_list = pd.Series(list(r.html.links))
    art_list = all_art_list[all_art_list.str.startswith("20")]
    logger.debug("Checked: %s", base_url + "_list.html")
    sleep(10)
    ret_articles = pd.concat([articles, art_list], ignore_index=True, names=[kind])
    return ret_articles


def get_description(base_domain: str, code: str, kind: str) -> pd.core.series.Series:
    session = HTMLSession()
    url = base_domain + code
    r = session.get(url)
    sleep(10)
    raw_title = r.html.find('title', first=True).text
    raw_article = r.html.find('article', first=True).text
    data_row = ["".join(a_text.replace("これは嘘ニュースです", "").replace("\n\n\n新しいアプリで記事を読む", "").split("\n"))
                for a_text in [raw_title, raw_article]]
    data = [code, kind] + data_row
    data_sr = pd.Series(data, index=["code", "kind", "title", "article"])
    return data_sr


def main():
    base_domain = "http://kyoko-np.net/"
    try:
        urls = pickle.load(open("urls.pickle", "rb"))
    except (OSError, IOError):
        kinds = ["national", "politics", "business", "sport",
                 "international", "science", "culture", "entertainment"]
        urls = pd.concat(
            [get_articles(base_domain, kind) for kind in kinds],
            axis=1, names=kinds
        )
        urls.columns = kinds
        pickle.dump(urls, open("urls.pickle", "wb"))
    df = pd.DataFrame(columns=["code", "kind", "title", "article"])
    for kind_name in urls:
        kind_urls = urls[kind_name]
        total = len(kind_urls)
        for i, code in enumerate(kind_urls):
            if code == nan or i > 3:
                break
            data_sr = get_description(base_domain, code, kind_urls.name)
            df = df.append(data_sr, ignore_index=True)
            logger.debug(
                "%d / %d done: %s, Category:%s", i, total, code, kind_name
            )
    df.to_csv("dataset_head.csv", sep=",")

if __name__ == '__main__':
    main()
