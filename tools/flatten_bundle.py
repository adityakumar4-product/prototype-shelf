#!/usr/bin/env python3
"""
Turn a self-unpacking prototype export into a plain static page.

The exports ship every asset as base64 inside the HTML and mint blob: URLs for
them at runtime. Blob-URL scripts are blocked in nested/sandboxed frames and on
file://, which is where "[bundle] resource failed to load: SCRIPT blob-..."
comes from. This writes the assets out as real files and rewrites the page to
reference them, so there is nothing left to unpack.

    python3 flatten_bundle.py <bundle.html> <out.html> <assets_dir>
"""
import base64
import gzip
import json
import mimetypes
import os
import re
import sys

EXT = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
    "image/svg+xml": ".svg", "image/gif": ".gif",
    "text/javascript": ".js", "application/javascript": ".js",
    "text/jsx": ".jsx", "text/babel": ".jsx", "application/json": ".json",
    "text/plain": ".txt",
    "text/css": ".css", "font/woff2": ".woff2", "font/woff": ".woff",
    "font/ttf": ".ttf", "text/html": ".html",
}


def island(src, name):
    tag = '<script type="__bundler/%s">' % name
    if tag not in src:
        return None
    i = src.index(tag) + len(tag)
    return src[i:src.index("</script>", i)]


def main(bundle, out_html, assets_dir):
    src = open(bundle, encoding="utf-8", errors="ignore").read()

    manifest = json.loads(island(src, "manifest"))
    template = json.loads(island(src, "template"))
    ext = json.loads(island(src, "ext_resources") or "[]")

    os.makedirs(assets_dir, exist_ok=True)
    rel = os.path.relpath(assets_dir, os.path.dirname(os.path.abspath(out_html)))

    written = {}
    for uuid, entry in manifest.items():
        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = gzip.decompress(raw)
        mime = entry.get("mime", "")
        ext_for = EXT.get(mime) or mimetypes.guess_extension(mime) or ".bin"
        name = uuid[:8] + ext_for
        with open(os.path.join(assets_dir, name), "wb") as f:
            f.write(raw)
        written[uuid] = (rel + "/" + name).replace(os.sep, "/")

    page = template
    # asset references appear as bare uuids in src=/href=
    for uuid, path in written.items():
        page = page.replace(uuid, path)

    page = re.sub(r'<script[^>]*type="__bundler/[^"]*"[^>]*>.*?</script>', "", page, flags=re.S)

    # The runtime resolves external resources (React/ReactDOM UMD, image slots)
    # through window.__resources, falling back to unpkg.com when it is missing.
    # The unpacker used to populate it; point it at the extracted files instead
    # so the page needs no network and no blob URLs.
    res = {e["id"]: written[e["uuid"]] for e in ext if e["uuid"] in written}
    shim = "<script>window.__resources=%s;</script>" % json.dumps(res)
    page = page.replace("<head>", "<head>\n" + shim, 1)

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(page)

    left = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", page)
    print("assets written : %d -> %s" % (len(written), assets_dir))
    print("page written   : %s (%.0f KB)" % (out_html, os.path.getsize(out_html) / 1024))
    print("unresolved uuid: %d" % len(set(left)))
    if left:
        print("  ", sorted(set(left))[:5])


if __name__ == "__main__":
    main(*sys.argv[1:4])
