#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
import re

BASE_URL = 'https://www.verbformen.de'

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


class VerbResponse:
    def __init__(self, html):
        self.konjugation = {}
        self.translations = {}

        soup = bs(html, 'html.parser')
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

                        self.konjugation[key] = f'\n{fixed_text}'
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
                self.translations[lang] = words
        except Exception as e:
            print(e)
        for v in konjugation.values():
            v.clear()

    def is_empty(self):
        return len(self.konjugation) == 0

    def to_string(self):
        result = "Einfache Verbformen:\n"
        for k, v in self.konjugation.items():
            result += f"*{k}*:{v}\n"
            result += '-' * 30 + '\n'
        result += "Übersetzungen:\n"
        for k, v in self.translations.items():
            result += f"*{k}*: {', '.join(v)}\n"
        return result


def remove_html_tags(word_with_tags):
    tags = ['<b>', '</b>', '<i>', '</i>', '<u>', '</u>', '<wbr/>']
    for t in tags:
        word_with_tags = word_with_tags.replace(t, '')
    return word_with_tags.strip()

class DeklinationResponse:
    def __init__(self, html):
        self.translations = {}
        soup = bs(html, 'html.parser')
        word_tag = soup.find('p', {'class': 'vGrnd rCntr'})
        self.word = word_tag.text.strip()

        word_forms_tag = soup.find('p', {'class': 'vStm rCntr'})
        self.word_forms = [word.strip() for word in word_forms_tag.text.split('\n') if
                           word.strip()
                           and word != '.'
                           and word != '·']

        deklination_tag = soup.find('section', {'class': 'rBox rBoxTrns'})
        chunks = []
        for line in deklination_tag.text.split('\n'):
            if 'Weitere Informationen finden sich' in line:
                pass
            elif line.startswith('Zusammenfassung'):
                pass
            elif line.startswith('Deklinationsformen'):
                pass
            elif line.startswith('Deklinationsformen'):
                pass
            elif line.startswith('Deklination'):
                pass
            else:
                chunks.append(line)
        self.deklination = re.sub(r"\n{2,}", "\n\n", '\n'.join(chunks))

        try:
            for lang in translations:
                words = set()
                for tag in soup.find('div', {'lang': lang}):
                    if type(tag) == Tag:
                        text = tag.text.strip()
                        if text and len(text) > 2:
                            words.add(text)
                self.translations[lang] = words
        except:
            pass

    def is_empty(self):
        return not self.word and not self.word_forms

    def to_string(self):
        result = f"*{self.word}*\n_"
        for word in self.word_forms:
            result += f"{word}; "
        result = result.rstrip("; ")
        result += '_'

        deklination = ''
        keywords = ['Nom.', 'Gen.', 'Dat.', 'Akk.', 'Positiv', 'Komparativ', 'Superlativ']
        for line in self.deklination.split('\n'):
            if ',' in line:
                deklination += f'*{line}*\n'
                deklination += '-' * 20
            elif any(k in line for k in keywords):
                deklination += '-' * 20 + '\n'
                deklination += f"_{line}_"
            else:
                deklination += line
            deklination += '\n'

        result += f'\n{deklination}'
        result += "Übersetzungen:\n"
        for k, v in self.translations.items():
            result += f"*{k}*: {', '.join(v)}\n"

        return result


def lookup_verbformen(query):
    url = f"{BASE_URL}/?w={query}"
    resp = requests.get(url, headers={
        'User-Agent': 'Your Mom'
    })
    if resp.ok:
        html = resp.text
        redirect_url = resp.request.url
        if 'konjugation' in redirect_url:
            return VerbResponse(html)
        elif 'deklination' in redirect_url:
            return DeklinationResponse(html)
        else:
            print(f'Unsupported redirect URL: {redirect_url}')
    else:
        print(resp.status_code)
