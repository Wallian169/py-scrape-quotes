import csv
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Callable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS_LIST = [field.name for field in fields(Quote)]


def timer(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> None:
        start = datetime.now()
        func(*args, **kwargs)
        end = datetime.now()
        elapsed_time = (end - start).total_seconds()
        print(f"Time elapsed: {elapsed_time : .6f} seconds")
    return inner


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_quotes_from_page(base_url: str) -> list[Quote]:
    text = requests.get(base_url).text
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    next_page = soup.select_one(".next a")
    while next_page:
        print(next_page)
        url_to_parse = urljoin(BASE_URL, next_page.get("href"))
        print(url_to_parse)
        text = requests.get(url_to_parse).text
        soup = BeautifulSoup(text, "html.parser")
        new_quotes = soup.select(".quote")
        quotes.extend(new_quotes)
        next_page = soup.select_one(".next a")

    return [parse_single_quote(quote) for quote in quotes]


def write_quotes_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS_LIST)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


@timer
def main(output_csv_path: str) -> None:
    print(f"Writing to {output_csv_path}")
    quotes_list = get_quotes_from_page(BASE_URL)
    write_quotes_to_csv(output_csv_path, quotes_list)


if __name__ == "__main__":
    main("quotes.csv")
