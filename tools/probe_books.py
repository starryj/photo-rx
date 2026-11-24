"""PDF/EPUB 体检：页数、文字层、图片数、判断策略。只读。"""
import sys, os, json
import pymupdf

ROOT = r"E:\03-Book\Photography"

def probe_pdf(path):
    doc = pymupdf.open(path)
    n = doc.page_count
    texts, imgs, big_pages = [], 0, 0
    sample = []
    for i in range(n):
        p = doc[i]
        t = p.get_text("text").strip()
        texts.append(len(t))
        try:
            il = p.get_images(full=True)
            imgs += len(il)
            if il:
                xref = il[0][0]
                info = doc.extract_image(xref)
                if info and len(info.get("image", b"")) > 200_000:
                    big_pages += 1
        except Exception:
            pass
        if i < 3:
            sample.append(t[:120].replace("\n", " / "))
    doc.close()
    nonempty = sum(1 for c in texts if c >= 40)
    total_chars = sum(texts)
    return dict(
        kind="pdf", pages=n,
        text_pages=nonempty,
        text_ratio=round(nonempty / n, 2) if n else 0,
        chars_total=total_chars,
        chars_per_page=round(total_chars / n, 0) if n else 0,
        images=imgs,
        big_image_pages=big_pages,
        sample=sample,
    )

def probe_epub(path):
    import zipfile, re
    z = zipfile.ZipFile(path)
    names = z.namelist()
    html = [n for n in names if n.lower().endswith((".html", ".xhtml", ".htm"))]
    images = [n for n in names if n.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))]
    chars = 0
    for n in html[:400]:
        try:
            raw = z.read(n).decode("utf-8", "ignore")
            txt = re.sub(r"<[^>]+>", " ", raw)
            chars += len(txt.strip())
        except Exception:
            pass
    z.close()
    return dict(kind="epub", html_files=len(html), images=len(images), chars_total=chars,
                chars_per_html=round(chars / max(1, len(html)), 0))

rows = []
for name in sorted(os.listdir(ROOT)):
    path = os.path.join(ROOT, name)
    if not os.path.isfile(path):
        continue
    try:
        r = probe_pdf(path) if name.lower().endswith(".pdf") else probe_epub(path)
    except Exception as e:
        r = dict(kind="error", error=str(e))
    r["file"] = name
    r["mb"] = round(os.path.getsize(path) / 1e6, 1)
    rows.append(r)

out = r"G:\AI_Workspace\04-MadeMySkills\photo-vision\probe.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

for r in rows:
    if r["kind"] == "pdf":
        print(f'{r["mb"]:>6.1f}MB {r["pages"]:>4}p 文字页{r["text_ratio"]:>5.0%} '
              f'{r["chars_per_page"]:>6.0f}字/页 图{r["images"]:>5} 大图页{r["big_image_pages"]:>4}  {r["file"][:40]}')
    elif r["kind"] == "epub":
        print(f'{r["mb"]:>6.1f}MB epub html{r["html_files"]:>4} 图{r["images"]:>4} '
              f'{r["chars_total"]:>7}字  {r["file"][:40]}')
    else:
        print("ERR", r.get("error"), r["file"][:40])
print("\n->", out)
