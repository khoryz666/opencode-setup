#!/usr/bin/env python3
"""Look up draw.io shape styles instead of guessing mxgraph.* names.

Searches draw.io's shape-library index, then its icon service for logos and
icons the libraries lack. Prints one "title widthxheight style" line per match.
"""

import json
import re
import sys
import urllib.parse
import urllib.request

INDEX_URL = "https://cdn.jsdelivr.net/gh/jgraph/drawio-mcp@main/shape-search/search-index.json"
ICON_SEARCH_URL = "https://icons.diagrams.net/api/icons/search?p=0&c=3&q="
ICON_STYLE_PREFIX = (
    "shape=image;html=1;verticalAlign=top;"
    "verticalLabelPosition=bottom;labelBackgroundColor=default;imageAspect=0;"
    "aspect=fixed;image="
)
LIMIT = 6
ABSOLUTE_IMAGE_RE = re.compile(r"(^|;)image=(?!https?:|data:)/?")
SAFE_ICON_URL_RE = re.compile(r"^https://[^;&\"'<>\s]+$")


def words(text: str) -> list[str]:
    return [word for word in re.split(r"\W+", text.lower()) if word]


def fetch_json(url: str, timeout: int) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "opencode-drawio-skill"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def absolute_image_url(style: str) -> str:
    return ABSOLUTE_IMAGE_RE.sub(r"\1image=https://app.diagrams.net/", style)


def search_icons(query: str) -> list[str]:
    try:
        data = fetch_json(ICON_SEARCH_URL + urllib.parse.quote(query, safe=""), 10)
    except Exception:
        return []
    images = data.get("images", []) if isinstance(data, dict) else []
    lines = []
    for image in images:
        url = image.get("url", "")
        if SAFE_ICON_URL_RE.match(url):
            lines.append(f"{image.get('title', 'icon')} 48x48 {ICON_STYLE_PREFIX}{url}")
    return lines


def main() -> None:
    queries = sys.argv[1:]
    if not queries:
        sys.exit('usage: find_shapes.py "aws4 lambda" "github" ...')

    try:
        index = fetch_json(INDEX_URL, 30)
    except Exception as error:
        sys.exit(f"find_shapes: could not load the shape index: {error}")

    for query in queries:
        terms = words(query)
        matches = []
        for shape in index:
            tags = words(shape.get("tags") or "")
            if terms and all(term in tags for term in terms):
                matches.append(
                    f"{shape.get('title', 'shape')} {shape.get('w')}x{shape.get('h')} "
                    f"{absolute_image_url(shape.get('style', ''))}"
                )
                if len(matches) >= LIMIT:
                    break
        if len(matches) < LIMIT:
            matches.extend(search_icons(query))
        print(f"# {query}")
        print("\n".join(matches) if matches else "(no match)")


if __name__ == "__main__":
    main()
