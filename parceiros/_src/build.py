#!/usr/bin/env python3
"""Gera as landings de parceiros (PT, EN, ES, DE) a partir de template.html + strings.py.

Uso: python3 parceiros/_src/build.py

Saída: parceiros/index.html, parceiros/en/index.html, parceiros/es/index.html, parceiros/de/index.html.
Os HTMLs gerados são versionados; o GitHub Pages só serve arquivos estáticos.
O Jekyll do GitHub Pages ignora pastas que começam com "_", então esta pasta não é publicada.
"""

import html
import re
import sys
from pathlib import Path
from urllib.parse import quote

from strings import LANGS

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
SITE_URL = "https://www.itacareecolodge.com.br/parceiros/"
DEFAULT_LANG = "pt"
TEXT_KEYS = set(LANGS[DEFAULT_LANG])


def page_url(lang):
    return SITE_URL + LANGS[lang]["path"]


def relative(from_lang, to_lang):
    """Caminho relativo entre as pastas de dois idiomas (todas ficam em parceiros/ ou parceiros/xx/)."""
    up = "../" if LANGS[from_lang]["path"] else ""
    return (up + LANGS[to_lang]["path"]) or "./"


def lang_nav(current):
    s = LANGS[current]
    base = "../" if s["path"] else ""
    items = []
    for code, t in LANGS.items():
        attrs = f'href="{relative(current, code)}" hreflang="{t["hreflang"]}" lang="{t["html_lang"]}"'
        if code == current:
            attrs += ' aria-current="page"'
        items.append(
            f'<li><a {attrs}>'
            f'<img src="{base}images/flags/{t["flag"]}.svg" alt="" width="20" height="15" />'
            f'<span class="lang-switch-code" aria-hidden="true">{t["code"]}</span>'
            f'<span class="visually-hidden">{t["name"]}</span>'
            f'</a></li>'
        )
    joined = "\n\t\t\t\t\t".join(items)
    return (
        f'<nav class="lang-switch" aria-label="{html.escape(s["lang_nav_label"])}">\n'
        f'\t\t\t\t<ul>\n\t\t\t\t\t{joined}\n\t\t\t\t</ul>\n\t\t\t</nav>'
    )


def alternates():
    links = [f'<link rel="alternate" hreflang="{t["hreflang"]}" href="{page_url(c)}" />' for c, t in LANGS.items()]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(DEFAULT_LANG)}" />')
    return "\n\t".join(links)


def render(template, lang):
    s = LANGS[lang]
    values = {k: html.escape(v, quote=True) for k, v in s.items()}
    values.update(
        base="../" if s["path"] else "",
        site_root="../../" if s["path"] else "../",
        url=page_url(lang),
        alternates=alternates(),
        og_locale_alternates="\n\t".join(
            f'<meta property="og:locale:alternate" content="{t["og_locale"]}" />'
            for c, t in LANGS.items() if c != lang
        ),
        lang_nav=lang_nav(lang),
        whatsapp_url="https://wa.me/5573999429945?text=" + quote(s["whatsapp_message"], safe="!"),
    )

    def sub(match):
        key = match.group(1)
        if key not in values:
            sys.exit(f"template.html usa uma chave desconhecida: {key}")
        return values[key]

    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def main():
    for lang, s in LANGS.items():
        missing = TEXT_KEYS - set(s)
        extra = set(s) - TEXT_KEYS
        if missing or extra:
            sys.exit(f"strings.py [{lang}]: faltando {sorted(missing)}, sobrando {sorted(extra)}")

    template = (SRC / "template.html").read_text(encoding="utf-8")
    for lang, s in LANGS.items():
        out = OUT / s["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template, lang), encoding="utf-8")
        print(f"{lang}: {out.relative_to(OUT.parent)}")


if __name__ == "__main__":
    main()
