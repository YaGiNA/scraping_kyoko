from requests_html import HTMLSession
from typing import List
from time import sleep


def get_articles(base_url: str) -> List[str]:
    session = HTMLSession()
    r = session.get(base_url + ".html")
    articles = [hit_url for hit_url in r.html.links if "20" in hit_url]
    sleep(15)
    r = session.get(base_url + "_list.html")
    list_articles = [hit_url for hit_url in r.html.links if "20" in hit_url]
    sleep(15)
    return articles.extend(list_articles)

def main():
    base_domain = "http://kyoko-np.net/"
    kinds = ["national", "politics", "business", "sport", "international", "science", "culture", "entertaiment"]
    url_list = [get_articles(base_domain + kind) for kind in kinds]
    print(url_list)

if __name__ == '__main__':
    main()
