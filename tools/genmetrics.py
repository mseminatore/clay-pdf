import sys, os, re
# usage: python3 tools/genmetrics.py <dir with the 14 AFM files> > src/metrics.clay
# (matplotlib ships them: matplotlib/mpl-data/fonts/pdfcorefonts; glyph names come
# from matplotlib._mathtext_data.uni2type1)
D = sys.argv[1].rstrip("/") + "/"

from matplotlib._mathtext_data import uni2type1
fonts = ["Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
         "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
         "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
         "Symbol", "ZapfDingbats"]
fallback = {"nbspace": "space", "sfthyphen": "hyphen", "uni00A0": "space", "uni00AD": "hyphen",
            "periodcentered": "periodcentered", "middot": "periodcentered", "mu1": "mu"}
out = []
for f in fonts:
    byname, bycode, hdr = {}, {}, {}
    for line in open(D + f + ".afm", encoding="latin-1"):
        if line.startswith("C "):
            parts = dict(p.strip().split(" ", 1) for p in line.strip().split(";") if p.strip())
            code = int(parts["C"]); w = int(float(parts["WX"])); n = parts["N"]
            byname[n] = w
            if code >= 0: bycode[code] = w
        else:
            m = re.match(r"(Ascender|Descender|CapHeight|XHeight) (-?\d+)", line)
            if m: hdr[m.group(1)] = int(m.group(2))
    widths = []
    missing = []
    symbolic = f in ("Symbol", "ZapfDingbats")
    for c in range(32, 256):
        if symbolic:
            widths.append(bycode.get(c, 0)); continue
        if c == 127: widths.append(0); continue
        try: ch = bytes([c]).decode("cp1252")
        except UnicodeDecodeError: widths.append(0); continue
        name = {0x20: "space", 0x2D: "hyphen", 0xA0: "space", 0xAD: "hyphen", 0xB5: "mu", 128: "Euro", 130: "quotesinglbase", 131: "florin", 132: "quotedblbase", 136: "circumflex", 152: "tilde", 164: "currency", 178: "twosuperior", 179: "threesuperior", 185: "onesuperior", 188: "onequarter", 190: "threequarters"}.get(c) or uni2type1.get(ord(ch))
        name = fallback.get(name, name)
        if name not in byname:
            missing.append((c, name)); widths.append(byname.get("bullet", 0) if False else 0); continue
        widths.append(byname[name])
    if missing: print(f, "missing", missing, file=sys.stderr)
    out.append((f, widths, hdr.get("Ascender", 0), hdr.get("Descender", 0), hdr.get("CapHeight", 0)))

print("""// Character widths of the 14 standard PDF fonts, generated from Adobe's
// Core 14 AFM files (see METRICS-LICENSE.txt; widths extracted, nothing else
// kept). widths: 1/1000 em per character code 32..255 -- Windows-1252 for the
// text fonts, the fonts' own encodings for Symbol and ZapfDingbats.
// ascent, descent, capHeight: 1/1000 em. Do not edit: regenerate instead.

PdfMetrics = Object clone {""")
def arr(ws):
    rows = [", ".join(str(w) for w in ws[i:i+16]) for i in range(0, len(ws), 16)]
    return "[\n            " + ",\n            ".join(rows) + "]"
print("    widths = #{")
print(",\n".join('        "%s": %s' % (f, arr(w)) for f, w, a, d, c in out))
print("    }")
print("    ascent = #{" + ", ".join('"%s": %d' % (f, a) for f, w, a, d, c in out) + "}")
print("    descent = #{" + ", ".join('"%s": %d' % (f, d) for f, w, a, d, c in out) + "}")
print("    capHeight = #{" + ", ".join('"%s": %d' % (f, c) for f, w, a, d, c in out) + "}")
print("}")
