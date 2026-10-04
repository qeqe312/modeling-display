"""Assemble source fragments into working HTML; package_demo.py must validate it."""
import argparse
from html import escape
from pathlib import Path
import sys

from deploy import atomic_write, reject_links, safe_file

REPO = Path(__file__).resolve().parent.parent
DEPENDENCY_START = '<!-- THREE_DEPENDENCY_START -->'
DEPENDENCY_END = '<!-- THREE_DEPENDENCY_END -->'


def assemble(source_dir, title, output, scripts=None):
    """Keep source fragments unchanged and combine ordered scripts in one tag."""
    source_dir = reject_links(source_dir)
    output = reject_links(output)
    template_path = reject_links(REPO / 'assets/template.html')
    if not source_dir.is_dir():
        raise ValueError('Source directory does not exist')
    if (output.resolve().is_relative_to(source_dir.resolve())
            or output.resolve() == template_path.resolve()):
        raise ValueError('Working HTML must be outside the source directory and template')
    if output.exists() and not output.is_file():
        raise ValueError('Output is not a file')

    css = safe_file(source_dir, 'style.css').read_text(encoding='utf-8')
    layout = safe_file(source_dir, 'layout.html').read_text(encoding='utf-8')
    script = '\n'.join(safe_file(source_dir, name).read_text(encoding='utf-8')
                       for name in (scripts if scripts is not None else ['app.js']))
    template = template_path.read_text(encoding='utf-8')
    if any(template.count(marker) != 1 for marker in (DEPENDENCY_START, DEPENDENCY_END)):
        raise ValueError('Expected one marked Three.js dependency block')

    # Locate all shell slots before inserting source text. Source contents may
    # repeat template strings, so replacements must never search the assembled page.
    title_start = template.index('<title>') + len('<title>')
    title_end = template.index('</title>', title_start)
    viewport_start = template.index('<meta name="viewport"')
    viewport_end = template.index('>', viewport_start) + 1
    comment_start = template.index('<!--', title_end)
    comment_end = template.index('-->', comment_start) + len('-->')
    style_start = template.index('<style>')
    style_end = template.index('</style>', style_start) + len('</style>')
    body_start = template.index('<body>') + len('<body>')
    dependency_start = template.index(DEPENDENCY_START, body_start)
    dependency_end = template.index(DEPENDENCY_END, dependency_start) + len(DEPENDENCY_END)
    script_start = template.rindex('<script>', dependency_end)
    script_end = template.index('</script>', script_start) + len('</script>')
    if not (title_end < comment_start < comment_end < style_start < style_end
            < body_start < dependency_start < dependency_end < script_start < script_end):
        raise ValueError('Unexpected template shell structure')

    slots = [
        (title_start, title_end, escape(title)),
        (viewport_start, viewport_end,
         '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'),
        (comment_start, comment_end,
         '<!-- Working HTML assembled from source fragments; validate and package before delivery. -->'),
        (style_start, style_end, '<style>\n' + css + '\n</style>'),
        (body_start, dependency_start, '\n' + layout + '\n'),
        (dependency_start, dependency_end,
         DEPENDENCY_START + '\n<script src="three.min.js"></script>\n' + DEPENDENCY_END),
        (script_start, script_end, '<script>\n' + script + '\n</script>'),
    ]
    for start, end, value in sorted(slots, reverse=True):
        template = template[:start] + value + template[end:]
    atomic_write(output, template.encode('utf-8'))
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--title', required=True)
    parser.add_argument('--script', action='append', help='Ordered source-relative JS; default: app.js')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        page = assemble(args.source_dir, args.title, args.output, args.script)
        print(f'Working HTML: {page}')
        print('Next: run package_demo.py with --inline to validate and package for delivery.')
        return 0
    except (OSError, ValueError) as error:
        print(f'Assembly failed: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
