import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('validator', Path(__file__).with_name('validate-packages.py'))
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
ROOT = Path(__file__).resolve().parent.parent


class PackageValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('manifests', 'packages'):
            shutil.copytree(ROOT / name, self.root / name)

    def test_published_packages_are_consistent(self):
        self.assertEqual(5, validator.validate(self.root))

    def test_rejects_original_graphql_identity_mismatch(self):
        path = self.root / 'manifests/graphql-api.json'
        manifest = json.loads(path.read_text())
        manifest.update(id='graphql', manifestUrl=manifest['manifestUrl'].replace('graphql-api.json', 'graphql.json'))
        path.unlink()
        (path.parent / 'graphql.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'package ID graphql-api differs'):
            validator.validate(self.root)

    def test_rejects_modified_package(self):
        with (self.root / 'packages/graphql-api-1.0.0.zip').open('ab') as package:
            package.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            validator.validate(self.root)


if __name__ == '__main__':
    unittest.main()
