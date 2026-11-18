# pdf

Write PDF files from Clay: pages, text in the 14 standard PDF fonts, lines,
rectangles, circles, polygons and Bezier paths, colors, dashes and clipping; text
measuring, word wrap, alignment, and a flow that starts new pages as it fills them.
Pure Clay, no native code.

```clay
import("pdf")

doc = Pdf new()                          // Letter; Pdf new("A4"), Pdf new([w, h])
doc title("Report") author("Me")
page = doc addPage()
page font("Helvetica-Bold", 18) text(72, 72, "Hello, PDF")
page strokeColor("#1f77b4") lineWidth(2) line(72, 90, 300, 90)
page fillColor(230, 230, 230) fillRect(72, 110, 200, 50)
doc save("hello.pdf")
```

`examples/hello.clay` draws one of everything; `examples/layout.clay` shows wrapping,
alignment, axis-style labels and page breaks.

### Flowing text

```clay
doc = Pdf new()
f = doc flow(72)                                   // 72-point margins
f font("Helvetica-Bold", 18) paragraph("Report", "center") space(8)
f font("Times-Roman", 11) paragraph(longText)        // wraps; new pages as needed
page = f ensure(200)                               // room for a 200-point figure
page rect(f x, f y, f width, 200)
f advance(200)
doc save("report.pdf")
```

## Coordinates

Units are points (1/72 inch). The origin is the **top-left** corner of the page and
y grows down, as in SVG and screen graphics; the library flips it for PDF. A text
position is the start of its baseline.

## API

**Document** (`Pdf`)

| Method | |
|---|---|
| `Pdf new(size = "letter")` | `"letter"`, `"legal"`, `"tabloid"`, `"a3"`, `"a4"`, `"a5"`, or `[width, height]` |
| `addPage(size = nil)` | A new page (the document's size unless given) |
| `title(s)`, `author(s)`, `subject(s)`, `creator(s)` | Document properties |
| `save(path)` | Write the file |
| `render` | The file as a (binary) string |
| `pages`, `pageCount` | |
| `flow(margin = 72)` | A `PdfFlow` on a new page |
| `Pdf textWidth(str, font, size)` | Width in points |
| `Pdf ascent(font, size)`, `descent(...)`, `capHeight(...)` | Heights in points (descent is negative) |
| `Pdf wrap(str, width, font, size)` | Lines no wider than width: breaks at spaces, inside over-long words, and at `"\n"` |

**Page** (every method returns the page, so calls chain)

| Method | |
|---|---|
| `font(name, size = 12)` | One of the 14 standard fonts: `Helvetica`, `Times-Roman`, `Courier` (each also `-Bold`, `-Oblique`/`-Italic`, `-BoldOblique`/`-BoldItalic`), `Symbol`, `ZapfDingbats` |
| `text(x, y, str, angle = 0)` | Text at (x, y); angle in degrees, counterclockwise |
| `textAlign("left" \| "center" \| "right")`, `textBaseline("alphabetic" \| "top" \| "middle" \| "bottom")` | Where `text` puts the text relative to (x, y), as in an HTML canvas; the offset turns with rotated text |
| `textWidth(str)`, `wrap(str, width)` | In the current font |
| `paragraph(x, y, width, str, align = "left", lineHeight = nil)` | Wrapped text in a box whose top is y; returns the y below it |
| `fillColor(r, g, b)`, `strokeColor(r, g, b)` | 0..255 each, or one `"#rrggbb"` string |
| `lineWidth(w)`, `dash([on, off, ...])`, `dash(nil)` | |
| `lineCap("butt" \| "round" \| "square")`, `lineJoin("miter" \| "round" \| "bevel")` | |
| `line(x1, y1, x2, y2)`, `polyline([[x, y], ...])` | Stroked |
| `rect(x, y, w, h)`, `fillRect(x, y, w, h)` | |
| `circle(cx, cy, r, fill = false, stroke = true)`, `ellipse(cx, cy, rx, ry, fill, stroke)` | |
| `polygon(points, fill = true, stroke = false)` | Closed |
| `moveTo`, `lineTo`, `curveTo(x1, y1, x2, y2, x, y)`, `closePath`, then `stroke`, `fill`, `fillStroke` | Paths |
| `save`, `restore`, `clipRect(x, y, w, h)` | Graphics state and clipping |
| `raw(ops)` | Content-stream operators as-is (PDF coordinates) |
| `width`, `height`, `fontName`, `fontSize` | |

**Flow** (`doc flow(margin)`)

| Method | |
|---|---|
| `font(name, size)`, `color(r, g, b)` / `color("#rrggbb")` / `color(nil)`, `lineHeight(h)` | Text style; carries over to new pages |
| `paragraph(str, align = "left")` | Wrapped across the page width; starts a new page when a line would cross the bottom margin |
| `space(h)` | Vertical space |
| `ensure(h)` | Starts a new page unless h points fit; returns the page to draw on at (`x`, `y`) |
| `advance(h)` | Move down past what you drew |
| `page`, `newPage`, `x`, `y`, `width`, `bottom` | |

## Text and characters

The standard fonts need no embedding, and every PDF reader has them. Their character
set is Windows-1252: ASCII plus Western European letters, curly quotes, dashes, `€`, `°`
and so on. UTF-8 text is mapped to it; characters outside it (Greek, CJK, emoji) are
written as `?`.

## Not yet

- Justified text, hyphenation and kerning
- Images (JPEG can be embedded as-is)
- Compressed streams (files are larger than they need to be)
- Embedded TrueType fonts, for any Unicode text
- Links, outlines/bookmarks, forms

## Develop

```sh
clay tests/test_pdf.clay       # a brick can import itself by name
clay examples/hello.clay       # writes hello.pdf
```

The tests check the file structure a reader depends on (the xref table's byte offsets,
each stream's `/Length`) as well as the drawing operators. `.github/workflows/test.yml`
runs them on Linux, macOS and Windows.

## License

MIT. The character widths in `src/metrics.clay` are extracted from Adobe's Core 14
AFM files (via `tools/genmetrics.py`); their notice is in `METRICS-LICENSE.txt`.
