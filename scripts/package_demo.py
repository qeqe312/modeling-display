"""Build a verified offline demo; --inline embeds Three.js in one HTML file."""
import argparse
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

from deploy import atomic_write, reject_links, safe_file

REPO = Path(__file__).resolve().parent.parent
THREE_SHA256 = "3a6602548c758cca4e2762d50e802a5400b4c663b6a638d76a9163598467ded4"


class DemoHTMLCheck(HTMLParser):
    """Reject active markup injected into textual template slots; not a JS sandbox."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.script_count = 0
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag in {'iframe', 'object', 'embed', 'base', 'svg', 'link', 'form'}:
            raise ValueError(f'Unexpected active/resource element: {tag}')
        attrs = dict(attrs)
        for name, value in attrs.items():
            if name.lower().startswith('on') or name.lower() in {'srcdoc', 'srcset', 'background', 'poster', 'ping'}:
                raise ValueError(f'Unexpected active attribute: {name}')
            normalized = ''.join((value or '').split()).lower()
            if name in {'href', 'src', 'action', 'formaction'} and normalized.startswith(('javascript:', 'data:')):
                raise ValueError('Unsafe URL in HTML')
            if name == 'style' and re.search(r'url\s*\(|@import', value or '', re.I):
                raise ValueError('External CSS resource is not allowed')
        if 'src' in attrs and not (tag == 'script' and attrs['src'] == 'three.min.js'):
            raise ValueError('Unexpected external resource')
        if tag == 'meta' and 'http-equiv' in attrs:
            raise ValueError('Unexpected HTTP-equivalent meta element')
        if tag == 'script':
            self.script_count += 1
        if tag == 'style':
            self.in_style = True

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style and re.search(r'url\s*\(|@import', data, re.I):
            raise ValueError('External CSS resource is not allowed')

    handle_startendtag = handle_starttag


def build(source, output, inline=False):
    source, output = reject_links(source), reject_links(output)
    if source.resolve().is_relative_to(output.resolve()):
        raise ValueError("Output must be separate from the source file/directory")
    html = source.read_text(encoding="utf-8")
    if re.search(r"__[A-Z0-9_]+__", html):
        raise ValueError("Fill all template placeholders before packaging")
    library = reject_links(REPO / "assets/vendor/three.min.js").read_bytes()
    if hashlib.sha256(library).hexdigest() != THREE_SHA256:
        raise ValueError("Bundled Three.js checksum mismatch")
    script = '<script src="three.min.js"></script>'
    if inline:
        script = '<script>' + library.decode("utf-8").replace('</script', '<\\/script') + '</script>'
    pattern = r'<!-- THREE_DEPENDENCY_START -->.*?<!-- THREE_DEPENDENCY_END -->'
    html, count = re.subn(pattern, lambda _: script, html, flags=re.S)
    if count != 1:
        raise ValueError("Expected one marked Three.js dependency block")
    checker = DemoHTMLCheck()
    checker.feed(html)
    checker.close()
    if checker.script_count != 2:
        raise ValueError('Expected only the verified library and one application script')
    files = {source.name: html.encode("utf-8"),
             "LICENSE": (REPO / "LICENSE").read_bytes(),
             "THREE-LICENSE.txt": (REPO / "assets/vendor/THREE-LICENSE.txt").read_bytes()}
    if not inline:
        files["three.min.js"] = library
    # Refuse accidental overwrite; use a fresh directory for each build.
    for name, content in files.items():
        path = safe_file(output, name)
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"Output already contains a different file: {name}")
    for name, content in files.items():
        atomic_write(safe_file(output, name), content)
    return output / source.name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--inline", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(build(args.source, args.output, args.inline))
        return 0
    except (OSError, ValueError) as error:
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
