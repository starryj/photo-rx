"""MinerU 本地 API 调用：单 PDF -> zip（md + content_list + images）。

用法:
  python mineru_call.py <pdf> <out_zip> [start_page] [end_page] [backend] [effort]
"""
import sys, time, os
import requests

API = "http://127.0.0.1:8000/file_parse"

def parse(pdf, out_zip, start=None, end=None, backend="hybrid-engine", effort="medium"):
    data = {
        "backend": backend,
        "effort": effort,
        "parse_method": "auto",
        "return_md": "true",
        "return_content_list": "true",
        "return_images": "true",
        "response_format_zip": "true",
        "image_analysis": "false",
    }
    if start is not None:
        data["start_page_id"] = str(start)
    if end is not None:
        data["end_page_id"] = str(end)

    t0 = time.time()
    with open(pdf, "rb") as f:
        files = {"files": (os.path.basename(pdf), f, "application/pdf")}
        r = requests.post(API, files=files, data=data, timeout=3600)
    dt = time.time() - t0
    if r.status_code != 200:
        print("HTTP", r.status_code, r.text[:500])
        return None
    with open(out_zip, "wb") as f:
        f.write(r.content)
    print(f"OK {dt:.1f}s  {len(r.content)/1e6:.2f} MB -> {out_zip}")
    return out_zip

if __name__ == "__main__":
    a = sys.argv[1:]
    pdf, out = a[0], a[1]
    start = int(a[2]) if len(a) > 2 and a[2] != "-" else None
    end = int(a[3]) if len(a) > 3 and a[3] != "-" else None
    backend = a[4] if len(a) > 4 else "hybrid-engine"
    effort = a[5] if len(a) > 5 else "medium"
    parse(pdf, out, start, end, backend, effort)
