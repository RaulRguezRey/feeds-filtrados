import os
import re
import feedparser
from xml.sax.saxutils import escape

FEED_URL = "https://www.directoalpaladar.com/feedburner.xml"
SALIDA = "docs/dap-recetas.xml"
PATRON_URL = re.compile(r"directoalpaladar\.com/(recetas-[^/]+|postres)/")


def es_receta(e):
    contenido = e.get("summary", "") + "".join(c.get("value", "") for c in e.get("content", []))
    return ("asset-recipe" in contenido
            or '"@type":"Recipe"' in contenido
            or bool(PATRON_URL.search(e.get("link", ""))))


feed = feedparser.parse(FEED_URL, sanitize_html=False)
items = []
for e in feed.entries:
    if not es_receta(e):
        continue
    items.append(
        "<item>"
        f"<title>{escape(e.get('title', ''))}</title>"
        f"<link>{escape(e.get('link', ''))}</link>"
        f"<guid>{escape(e.get('id', e.get('link', '')))}</guid>"
        f"<pubDate>{escape(e.get('published', ''))}</pubDate>"
        f"<description>{escape(e.get('summary', ''))}</description>"
        "</item>"
    )

rss = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<rss version="2.0"><channel>'
    "<title>Directo al Paladar - Solo recetas</title>"
    "<link>https://www.directoalpaladar.com</link>"
    "<description>Feed filtrado: solo recetas</description>"
    + "".join(items)
    + "</channel></rss>"
)

os.makedirs("docs", exist_ok=True)
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write(rss)
print(f"{len(items)} recetas de {len(feed.entries)} articulos")
