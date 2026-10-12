from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent


def build_backend():
    """Bundle pinned dependencies without changing the developer's local links."""
    bun = shutil.which('bun')
    if bun is None:
        raise RuntimeError('Building gum-jsx from source requires Bun 1.4.2 or newer.')
    backend = ROOT / 'gum' / 'js'
    with TemporaryDirectory(prefix='gum-jsx-build-') as directory:
        source = Path(directory)
        for pattern in ('*.ts', 'package.json', 'bun.lock'):
            for path in backend.glob(pattern):
                shutil.copy2(path, source / path.name)
        # The postinstall script builds JavaScript, fonts, and dependency notices.
        subprocess.run([bun, 'install', '--frozen-lockfile', '--production'],
                       cwd=source, check=True)
        destination = backend / 'build'
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(source / 'build', destination)


class BuildPy(build_py):
    """Build the backend before collecting the wheel's package data."""

    def run(self):
        build_backend()
        # Remove assets left by earlier builds before copying the current bundle.
        shutil.rmtree(Path(self.build_lib) / 'gum' / 'js', ignore_errors=True)
        super().run()


setup(cmdclass={'build_py': BuildPy})
