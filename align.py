#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Align Parallel Corpora using WebAlignToolkit

http://phraseotext.univ-grenoble-alpes.fr/webAlignToolkit/

@author: Hrishikesh Terdalkar
"""

###############################################################################

import logging
from typing import Dict, List

import requests
import pandas as pd
from bs4 import BeautifulSoup

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################

LANGUAGES = {
    "ab": "Abkhazian",
    "af": "Afrikaans",
    "ar": "Arabic",
    "az": "Azerbaijani",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bo": "Tibetan",
    "br": "Breton",
    "ca": "Catalan, Valencian",
    "ceb": "Cebuano",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Modern Greek",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish, Castilian",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fo": "Faroese",
    "fr": "French",
    "fy": "Western Frisian",
    "gd": "Scottish Gaelic, Gaelic",
    "gl": "Galician",
    "gu": "Gujarati",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Central Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "ku": "Kurdish",
    "ky": "Kirghiz, Kyrgyz",
    "la": "Latin",
    "lo": "Lao",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay (macrolanguage)",
    "nd": "North Ndebele",
    "ne": "Nepali",
    "nl": "Dutch, Flemish",
    "nn": "Norwegian Nynorsk",
    "no": "Norwegian",
    "nso": "Pedi, Northern Sotho, Sepedi",
    "or": "Oriya",
    "pa": "Panjabi, Punjabi",
    "pl": "Polish",
    "ps": "Pushto, Pashto",
    "pt": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "pt-PT": "Portuguese (Portugal)",
    "ro": "Romanian, Moldavian, Moldovan",
    "ru": "Russian",
    "sa": "Sanskrit",
    "sh": "Serbo-Croatian",
    "si": "Sinhala, Sinhalese",
    "sk": "Slovak",
    "sl": "Slovenian, Slovene",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili (macrolanguage)",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Tagalog",
    "tlh": "Klingon, tlhIngan-Hol",
    "tn": "Tswana, Setswana",
    "tr": "Turkish",
    "ts": "Tsonga",
    "tw": "Twi",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "ve": "Venda",
    "vi": "Vietnamese",
    "xh": "Xhosa",
    "zh": "Chinese",
    "zh-TW": "Chinese (Taiwan)",
    "zu": "Zulu"
}

ALIGNERS = [
    "LF Aligner",
    "YASA",
    "JAM",
    "Alinea Lite"
]

DEFAULT_ALIGNER = "YASA"

###############################################################################


class Aligner:
    SERVER = "http://phraseotext.univ-grenoble-alpes.fr"
    PATH = "webAlignToolkit"
    SITEMAP = {
        "align_text": "alignText.php"
    }

    def __init__(self, aligner: str = None):
        self.aligner = aligner or DEFAULT_ALIGNER
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) "
                           "Gecko/20100101 Firefox/92.0"),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Origin": self.SERVER,
            "Referer": f"{self.SERVER}/{self.PATH}",
            "Sec-GPC": "1"
        }

    def align(self, language_data: Dict) -> str:
        url = self.get_url("align_text")
        data = {
            "aligner_direct": self.aligner,
            "sessionId": ""
        }

        for idx, (lang_id, lang_data) in enumerate(language_data.items()):
            lang_name = LANGUAGES[lang_id]

            data[f"l{idx+1}"] = lang_data
            data[f"l{idx+1}Language"] = f"{lang_name}+({lang_id})"

        r = self.session.post(url, data=data)

        tmx_url = f"{self.SERVER}{r.content.decode()}"
        r_tmx = self.session.get(tmx_url)
        tmx_content = r_tmx.content.decode()

        return self.parse_tmx(tmx_content)

    def get_url(self, key: str) -> str:
        return f"{self.SERVER}/{self.PATH}/{self.SITEMAP[key]}"

    @staticmethod
    def parse_tmx(tmx_content: str) -> List[Dict[str, str]]:
        table = []
        soup = BeautifulSoup(tmx_content, "lxml")
        rows = soup.find_all("tu")
        for row in rows:
            row_dict = {}
            row_dict['id'] = row['tuid']
            for cell in row.find_all("tuv"):
                row_dict[cell["xml:lang"]] = cell.get_text().strip()

            table.append(row_dict)
        return table


###############################################################################


def main():
    import os
    import argparse

    parser = argparse.ArgumentParser(
        description="Align Sentences using WebAlignToolkit"
    )
    parser.add_argument("language_file", nargs="+", help="language files")
    parser.add_argument("-o", "--output", type=str, help="path to output")
    parser.add_argument("-a", "--aligner", type=str, help="specify aligner")
    parser.add_argument(
        "--verbose", action="store_true", help="turn on verbose output"
    )
    parser.add_argument(
        "--debug", action="store_true", help="turn on debug mode"
    )
    args = vars(parser.parse_args())

    language_files = args.get("language_file")
    output_file = args.get("output")
    aligner = args.get("aligner")

    # ----------------------------------------------------------------------- #

    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        root_logger.addHandler(logging.StreamHandler())

    if args.get("verbose"):
        root_logger.setLevel(logging.INFO)
    if args.get("debug"):
        root_logger.setLevel(logging.DEBUG)

    # ----------------------------------------------------------------------- #

    if len(language_files) < 2:
        parser.error("Must provide at least 2 language files.")

    if aligner and aligner not in ALIGNERS:
        parser.error(f"Invalid aligner. Valid options: {ALIGNERS}")

    # ----------------------------------------------------------------------- #

    A = Aligner(aligner)

    language_data = {}

    for language_file in language_files:
        lang_id = os.path.basename(language_file).split("-", 1)[0]
        if lang_id not in LANGUAGES:

            parser.error(
                f"Could not detect the language from `{language_file}'\n"
                "Language files must start with `lang_id-', e.g. 'sa-1.txt'"
            )

        with open(language_file) as f:
            lang_data = f.read()
        language_data[lang_id] = lang_data

    if not output_file:
        output_file = "-".join(language_data.keys())

    if not output_file.endswith(".xlsx"):
        output_file = f"{output_file}.xlsx"

    aligned_data = A.align(language_data)

    df = pd.DataFrame(aligned_data)
    df.to_excel(output_file, index=False)

    return 0

###############################################################################


if __name__ == "__main__":
    import sys
    sys.exit(main())

###############################################################################
