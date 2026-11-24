#!/usr/bin/env python3
"""Small assert-based self-check for the drawio helper scripts."""

from drawio_url import make_url
from find_shapes import absolute_image_url, words
from repair_drawio import repair


def main() -> None:
    dirty = (
        "noise <mxGraphModel><root>"
        '<mxCell id="1" parent="1"/>'
        '<mxCell id="2" parent="1" value="R&D &amp; more"/>'
        "</root></mxGraphModel> tail"
    )
    fixed = repair(dirty)
    assert fixed.startswith("<mxGraphModel>")
    assert fixed.endswith("</mxGraphModel>")
    assert 'parent="0"' in fixed
    assert "R&amp;D" in fixed

    url = make_url("<mxGraphModel><root/></mxGraphModel>")
    assert url.startswith("https://app.diagrams.net/?")
    assert "#R" in url

    assert words("AWS4 Lambda!") == ["aws4", "lambda"]
    assert absolute_image_url("image=img/lib/aws4/lambda.svg").endswith(
        "image=https://app.diagrams.net/img/lib/aws4/lambda.svg"
    )

    print("drawio helpers: ok")


if __name__ == "__main__":
    main()
