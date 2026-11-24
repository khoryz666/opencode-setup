#!/usr/bin/env python3
"""Print a draw.io editor URL for a .drawio file.

The file stays local. The URL carries the compressed XML in its #R fragment,
so no draw.io Desktop install is needed just to view or edit it.
"""

import base64
import sys
import urllib.parse
import zlib
from pathlib import Path

URL_PREFIX = "https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#R"
SAFE = "-_.!~*'()"


def make_url(xml: str) -> str:
    encoded = urllib.parse.quote(xml, safe=SAFE)
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = compressor.compress(encoded.encode("utf-8")) + compressor.flush()
    compressed = base64.b64encode(data).decode("ascii")
    return URL_PREFIX + urllib.parse.quote(compressed, safe=SAFE)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: drawio_url.py FILE.drawio")
    path = Path(sys.argv[1])
    try:
        xml = path.read_text(encoding="utf-8")
    except OSError as error:
        sys.exit(f"drawio_url: {error}")
    print(make_url(xml))


if __name__ == "__main__":
    main()
