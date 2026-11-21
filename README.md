# pdf

Write PDF files from Clay: pages, text in the 14 standard PDF fonts, lines,
rectangles, circles, polygons and Bezier paths, colors, transparency, dashes and
clipping; PNG and JPEG images; text measuring, word wrap, alignment, and a flow that
starts new pages as it fills them. clay-plot uses it to save figures as PDF.
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
alignment, axis-style labels and page breaks; `examples/images.clay` shows images
and transparency.

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
| `Pdf wrapRuns(runs, width, size)` | Rich text -- runs `[text, font]` or `[text, font, "#rrggbb"]` -- broken into lines at spaces (a word may span runs); each line is `[pieces, width]` for `page runs`. A run's fourth element, `#{scale: 0.7, rise: 0.4}`, makes it smaller and raises it (in ems of the size; negative lowers it), for super- and subscripts |
| `loadImage(path)` | A `.png`, `.jpg` or `.jpeg` file as an image to draw |
| `png(bytes)`, `jpeg(bytes)` | The same from a file's bytes |
| `image(w, h, channels, pixels)` | From 8-bit pixels, row by row: 1 gray, 2 gray + alpha, 3 RGB, 4 RGBA |

**Page** (every method returns the page, so calls chain)

| Method | |
|---|---|
| `font(name, size = 12)` | One of the 14 standard fonts: `Helvetica`, `Times-Roman`, `Courier` (each also `-Bold`, `-Oblique`/`-Italic`, `-BoldOblique`/`-BoldItalic`), `Symbol`, `ZapfDingbats` |
| `text(x, y, str, angle = 0)` | Text at (x, y); angle in degrees, counterclockwise |
| `textAlign("left" \| "center" \| "right")`, `textBaseline("alphabetic" \| "top" \| "middle" \| "bottom")` | Where `text` puts the text relative to (x, y), as in an HTML canvas; the offset turns with rotated text |
| `textWidth(str)`, `wrap(str, width)` | In the current font |
| `runs(x, y, pieces, size)` | One line of rich text from `Pdf wrapRuns` with its baseline at (x, y); returns its width |
| `paragraph(x, y, width, str, align = "left", lineHeight = nil)` | Wrapped text in a box whose top is y; returns the y below it |
| `fillColor(r, g, b)`, `strokeColor(r, g, b)` | 0..255 each, or one `"#rrggbb"` string |
| `lineWidth(w)`, `dash([on, off, ...])`, `dash(nil)` | |
| `lineCap("butt" \| "round" \| "square")`, `lineJoin("miter" \| "round" \| "bevel")` | |
| `line(x1, y1, x2, y2)`, `polyline([[x, y], ...])` | Stroked |
| `rect(x, y, w, h)`, `fillRect(x, y, w, h)` | |
| `circle(cx, cy, r, fill = false, stroke = true)`, `ellipse(cx, cy, rx, ry, fill, stroke)` | |
| `polygon(points, fill = true, stroke = false)` | Closed |
| `moveTo`, `lineTo`, `curveTo(x1, y1, x2, y2, x, y)`, `closePath`, then `stroke`, `fill`, `fillStroke` | Paths |
| `image(img, x, y, w = nil, h = nil, opts = nil)` | An image with its top-left corner at (x, y), stretched to w x h points (default: a point per pixel); `#{flipY: true}` draws it upside down |
| `alpha(fill, stroke = nil)` | Opacity 0..1 of fills and text, and of strokes (default: the same); lasts until changed or `restore` |
| `save`, `restore`, `clipRect(x, y, w, h)` | Graphics state and clipping |
| `raw(ops)` | Content-stream operators as-is (PDF coordinates) |
| `width`, `height`, `fontName`, `fontSize` | |

**Flow** (`doc flow(margin)`)

| Method | |
|---|---|
| `font(name, size)`, `color(r, g, b)` / `color("#rrggbb")` / `color(nil)`, `lineHeight(h)` | Text style; carries over to new pages |
| `paragraph(str, align = "left")` | Wrapped across the page width; starts a new page when a line would cross the bottom margin |
| `richParagraph(runs, align = "left", indent = 0)` | The same for rich text (runs as for `Pdf wrapRuns`), at the flow's font size; `indent` narrows it from the left |
| `space(h)` | Vertical space |
| `ensure(h)` | Starts a new page unless h points fit; returns the page to draw on at (`x`, `y`) |
| `advance(h)` | Move down past what you drew |
| `page`, `newPage`, `x`, `y`, `width`, `bottom` | |

## Images

```clay norun
logo = doc loadImage("logo.png")
page image(logo, 72, 72, 144, 48)
page image(logo, 72, 140)                         // a point per pixel
```

PNG and JPEG data goes into the file still compressed, without being decoded: JPEG as
it is, and PNG's zlib data with its row predictors (PDF reads both). That covers gray,
RGB and palette PNGs that are not interlaced. A PNG with an alpha channel has to be
decoded first, so pass its pixels to `doc image` instead (clay-image's `img pixels`).
Raw pixels are stored uncompressed; an alpha channel becomes a soft mask, and
`img mask(grayImage)` sets one by hand. An image drawn several times is stored once.
Viewers may smooth an image they enlarge; to keep pixels sharp, enlarge it before
embedding. `examples/images.clay` draws each kind.

## Text and characters

The standard fonts need no embedding, and every PDF reader has them. Their character
set is Windows-1252: ASCII plus Western European letters, curly quotes, dashes, `€`, `°`
and so on. UTF-8 text is mapped to it; characters outside it (Greek, CJK, emoji) are
written as `?`.

## Not yet

- Justified text, hyphenation and kerning
- Compressed content streams and raw-pixel images (PNG and JPEG stay compressed)
- Interlaced PNGs, and PNGs with alpha without decoding them first
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
