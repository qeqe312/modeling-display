from contextlib import redirect_stderr, redirect_stdout
from html import escape
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import assemble_demo
import package_demo


class AssembleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='geo3d-assemble-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        (self.source / 'style.css').write_text('body { color: red; }', encoding='utf-8')
        (self.source / 'layout.html').write_text('<main>Test layout</main>', encoding='utf-8')
        (self.source / 'app.js').write_text('window.example = true;', encoding='utf-8')

    def test_both_retained_examples_assemble_and_package_without_source_changes(self):
        examples = [
            ('外接球题建模示例', None),
            ('正四棱台2023真题演示', ['model.js', 'engine.js']),
        ]
        for title, scripts in examples:
            with self.subTest(example=title):
                source = ROOT / 'examples' / title / '开发资料' / '源码'
                originals = {p: p.read_bytes() for p in source.iterdir() if p.is_file()}
                page = assemble_demo.assemble(source, title, self.base / (title + '.html'), scripts)
                html = page.read_text(encoding='utf-8')
                self.assertIn(source.joinpath('style.css').read_text(encoding='utf-8'), html)
                self.assertIn(source.joinpath('layout.html').read_text(encoding='utf-8'), html)
                script = '\n'.join(source.joinpath(name).read_text(encoding='utf-8')
                                   for name in (scripts or ['app.js']))
                self.assertIn('<script>\n' + script + '\n</script>', html)
                packaged = package_demo.build(page, self.base / title, inline=True)
                final = packaged.read_text(encoding='utf-8')
                checker = package_demo.DemoHTMLCheck()
                checker.feed(final)
                checker.close()
                self.assertEqual(checker.script_count, 2)
                self.assertNotIn('cdn.jsdelivr.net', final)
                self.assertNotIn('user-scalable=no', final)
                self.assertNotIn('maximum-scale=1', final)
                self.assertNotIn('引擎部分（D 之后）已验证，不要改', final)
                self.assertNotIn('引擎每帧重建时会调用它', final)
                self.assertFalse((packaged.parent / 'three.min.js').exists())
                self.assertTrue((packaged.parent / 'LICENSE').is_file())
                self.assertTrue((packaged.parent / 'THREE-LICENSE.txt').is_file())
                self.assertEqual(originals, {p: p.read_bytes() for p in originals})

    def test_cli_script_order_shared_scope_title_escape_and_atomic_rebuild(self):
        (self.source / 'model.js').write_text('(function(){\nconst order = ["model"];', encoding='utf-8')
        (self.source / 'engine.js').write_text('order.push("engine");\nwindow.order=order;\n})();', encoding='utf-8')
        title = '<demo> & "quoted"'
        output = self.base / 'working.html'
        args = ['--source-dir', str(self.source), '--title', title,
                '--script', 'model.js', '--script', 'engine.js', '--output', str(output)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(assemble_demo.main(args), 0)
        first = output.read_bytes()
        html = first.decode('utf-8')
        self.assertIn('<title>' + escape(title) + '</title>', html)
        self.assertIn('const order = ["model"];\norder.push("engine");', html)
        self.assertEqual(html.count('<script>'), 1)
        self.assertNotIn('__TITLE__', html)
        output.write_text('stale working HTML', encoding='utf-8')
        with redirect_stdout(io.StringIO()):
            self.assertEqual(assemble_demo.main(args), 0)
        self.assertEqual(output.read_bytes(), first)
        self.assertFalse(list(self.base.glob('.deploy-*')))

    def test_default_script_nested_script_and_no_whole_page_replacement(self):
        # Shell-like text in a source fragment must survive unchanged.
        layout = '<main><span>__TITLE__</span><code>&lt;style&gt;</code></main>'
        (self.source / 'layout.html').write_text(layout, encoding='utf-8')
        output = assemble_demo.assemble(self.source, 'Page title', self.base / 'default.html')
        html = output.read_text(encoding='utf-8')
        self.assertIn(layout, html)
        self.assertIn('<script>\nwindow.example = true;\n</script>', html)
        nested = self.source / 'parts'
        nested.mkdir()
        (nested / 'logic.js').write_text('window.nested = true;', encoding='utf-8')
        output = assemble_demo.assemble(self.source, 'Nested', self.base / 'nested.html', ['parts/logic.js'])
        self.assertIn('window.nested = true;', output.read_text(encoding='utf-8'))

    def test_unsafe_script_paths_and_source_overwrite_are_refused_before_writing(self):
        unsafe = ['../app.js', '/app.js', 'C:/app.js', 'parts\\app.js', 'parts/../app.js', './app.js']
        for name in unsafe:
            with self.subTest(script=name):
                output = self.base / 'blocked.html'
                with self.assertRaises(ValueError):
                    assemble_demo.assemble(self.source, 'Unsafe', output, [name])
                self.assertFalse(output.exists())
        original = (self.source / 'app.js').read_bytes()
        for output in [self.source / 'app.js', self.source / 'new.html', ROOT / 'assets/template.html']:
            with self.subTest(output=output):
                with self.assertRaises(ValueError):
                    assemble_demo.assemble(self.source, 'Unsafe', output)
        self.assertEqual((self.source / 'app.js').read_bytes(), original)
        self.assertFalse((self.source / 'new.html').exists())

    def test_linked_source_or_output_is_refused(self):
        linked = self.source / 'linked.js'
        try:
            linked.symlink_to(self.source / 'app.js')
        except (OSError, NotImplementedError) as error:
            self.skipTest(f'Local symbolic links unavailable: {error}')
        output = self.base / 'blocked.html'
        with self.assertRaises(ValueError):
            assemble_demo.assemble(self.source, 'Linked source', output, ['linked.js'])
        self.assertFalse(output.exists())
        linked_output = self.base / 'linked-output.html'
        linked_output.symlink_to(self.source / 'app.js')
        with self.assertRaises(ValueError):
            assemble_demo.assemble(self.source, 'Linked output', linked_output)
        self.assertEqual((self.source / 'app.js').read_text(encoding='utf-8'), 'window.example = true;')

    def test_windows_reparse_attributes_are_refused_without_link_creation_privileges(self):
        # Simulate Windows filesystem metadata on an ordinary local fixture so
        # this safety gate is exercised even on systems unable to create links.
        original_lstat = Path.lstat
        marked = self.source / 'app.js'

        def lstat(path, *args, **kwargs):
            info = original_lstat(path, *args, **kwargs)
            if path == marked:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
            return info

        output = self.base / 'blocked.html'
        with patch.object(Path, 'lstat', autospec=True, side_effect=lstat):
            with self.assertRaisesRegex(ValueError, 'link/reparse'):
                assemble_demo.assemble(self.source, 'Reparse source', output)
        self.assertFalse(output.exists())
        output.write_text('keep this file', encoding='utf-8')
        marked = output
        with patch.object(Path, 'lstat', autospec=True, side_effect=lstat):
            with self.assertRaisesRegex(ValueError, 'link/reparse'):
                assemble_demo.assemble(self.source, 'Reparse output', output)
        self.assertEqual(output.read_text(encoding='utf-8'), 'keep this file')

    def test_cli_reports_missing_source_without_creating_output(self):
        output = self.base / 'blocked.html'
        with redirect_stderr(io.StringIO()) as errors:
            code = assemble_demo.main(['--source-dir', str(self.base / 'missing'), '--title', 'Missing',
                                       '--output', str(output)])
        self.assertEqual(code, 2)
        self.assertIn('Assembly failed:', errors.getvalue())
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
