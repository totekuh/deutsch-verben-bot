#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as bs
from bs4.element import Tag

BASE_URL = 'https://www.verbformen.de/konjugation'

konjugation = {
    'Präsens': [],
    'Präteritum': [],
    # 'Imperativ': [],
    # 'Konjunktiv I': [],
    # 'Konjunktiv II': [],
    # 'Infinitiv': [],
    'Partizip': [],
}

translations = [
    'en',
    'ru'
]

pronounces = [
    'ich',
    'du',
    'er',
    'wir',
    'ihr',
    'sie'
]


class VerbformenResponse:
    def __init__(self):
        self.konjugation = {}
        self.transactions = {}

    def is_empty(self):
        return len(self.konjugation) == 0 or len(self.transactions) == 0

    def to_string(self):
        result = "Einfache Verbformen:\n"
        for k, v in self.konjugation.items():
            result += f"*{k}*:{v}\n"
            result += '-' * 30 + '\n'
        result += "Übersetzungen:\n"
        for k, v in self.transactions.items():
            result += f"*{k}*: {', '.join(v)}\n"
        return result


def parse_verben_page(html):
    soup = bs(html, 'html.parser')
    verbformen_response = VerbformenResponse()
    try:
        for tag in soup.find_all('div', {'class': 'vTbl'}):
            text = tag.text
            for key in konjugation.keys():
                if key.lower() in text.lower() and not konjugation[key]:
                    fixed_text = text \
                        .replace(key, '') \
                        .replace('\n', ' ') \
                        .strip()
                    if any(f" {pr} " in fixed_text for pr in pronounces):
                        for pr in pronounces[1:]:
                            fixed_text = fixed_text \
                                .replace(f" {pr} ", f"\n{pr} ")
                    else:
                        fixed_text = fixed_text.replace(' ', '\n')
                    konjugation[key].append(fixed_text)

                    verbformen_response.konjugation[key] = f'\n{fixed_text}'
    except Exception as e:
        print(e)
    try:
        for lang in translations:
            words = set()
            for tag in soup.find('div', {'lang': lang}):
                if type(tag) == Tag:
                    text = tag.text.strip()
                    if text and len(text) > 2:
                        words.add(text)
            verbformen_response.transactions[lang] = words
    except Exception as e:
        print(e)
    for v in konjugation.values():
        v.clear()
    return verbformen_response


def lookup_verbformen(query):
    url = f"{BASE_URL}/?w={query}"
    resp = requests.get(url)
    if resp.ok:
        return parse_verben_page(resp.text)
    else:
        print(resp.status_code)
