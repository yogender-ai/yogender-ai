"""Publish an SVG under a content-hashed file name and point the README at it.

GitHub serves README images from raw.githubusercontent.com under their plain
path (any ?query is dropped by the redirect), so a browser that saw the old
picture keeps showing it. A new file name whenever the picture changes is the
only thing that reliably shows visitors the current one.

    publish("wall", svg_text)  ->  assets/live/wall-<hash>.svg, README updated
"""
import hashlib
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIVE = os.path.join(ROOT, "assets", "live")
README = os.path.join(ROOT, "README.md")


def publish(name, body):
    digest = hashlib.sha1(body.encode("utf-8")).hexdigest()[:10]
    target = f"{name}-{digest}.svg"
    os.makedirs(LIVE, exist_ok=True)
    for f in os.listdir(LIVE):
        if re.fullmatch(rf"{re.escape(name)}-[0-9a-f]{{10}}\.svg", f) and f != target:
            os.remove(os.path.join(LIVE, f))
    with open(os.path.join(LIVE, target), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    try:
        with open(README, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        return target
    pattern = rf'src="\./assets/(?:live/)?{re.escape(name)}(?:-[0-9a-f]{{10}})?\.svg(?:\?[^"]*)?"'
    new = re.sub(pattern, f'src="./assets/live/{target}"', text)
    if new != text:
        with open(README, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)
    return target
