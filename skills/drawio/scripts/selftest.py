#!/usr/bin/env python3
"""Small assert-based self-check for the drawio helper scripts."""

import tempfile
from pathlib import Path

from diagram import Diagram
from drawio_url import make_url
from find_shapes import absolute_image_url, words
from lint_drawio import lint
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

    with tempfile.TemporaryDirectory() as tmp:
        d = Diagram("p", 2245, 3179)
        a = d.box(100, 100, 400, 200, "A &amp; B", size=32)
        b = d.text(2000, 100, 400, 100, "<b>off page</b>", size=18)
        d.arrow(a, b, label="x")
        d.line(0, 0, 10, 10)
        path = Path(tmp) / "p.drawio"
        d.save(path)
        problems = lint(path)
        assert len(problems) == 2, problems
        assert "c3 at" in problems[0] and "outside" in problems[0] and "font 18px < 24px" in problems[1]
        assert lint(path, 10) == [problems[0]]
        path.write_text(d.xml().replace('target="c3"', 'target="c9"'))
        assert any("target c9 does not exist" in p for p in lint(path, 0))

    print("drawio helpers: ok")


if __name__ == "__main__":
    main()
