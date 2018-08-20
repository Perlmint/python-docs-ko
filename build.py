#!/usr/bin/env python3
import os
import subprocess
import sys

VERSION = '3.7'


def shell(cmd, capture=False, chdir=None):
    opts = {
        'shell': True,
        'stdin': subprocess.PIPE,
    }
    cwd = os.getcwd() if chdir else None
    if chdir:
        os.chdir(chdir)
    try:
        if capture:
            opts['stderr'] = subprocess.STDOUT
            opts['universal_newlines'] = True
            return subprocess.check_output(cmd, **opts)
        else:
            return subprocess.check_call(cmd, **opts)
    finally:
        if cwd:
            os.chdir(cwd)


def git_clone(repository, directory, branch=None):
    if not os.path.exists(directory):
        shell("git clone --depth 1 --no-single-branch {} {}".format(repository, directory))
    if branch:
        shell("git -C {} checkout {}".format(directory, branch))
    shell("git -C {} pull".format(directory))

def prepare_env():
    git_clone('https://github.com/python/cpython.git', 'cpython', VERSION)

    locale_dir = os.path.join('cpython', 'locale', 'ko', 'LC_MESSAGES')
    if not os.path.exists(locale_dir):
        locale_repo = shell('git config --get remote.origin.url', capture=True).strip()
        git_clone(locale_repo, locale_dir, VERSION)


def build():
    doc_dir = os.path.join('cpython', 'Doc')
    sphinx_opts = "-D locale_dirs=../locale -D language=ko -D gettext_compact=0"
    if sys.platform == 'win32':
        backup_sphinxopts = os.environ['SPHINXOPTS']
        os.environ['SPHINXOPTS'] = sphinx_opts + " -Ea -A daily=1 -A switchers=1"
        shell(
            "make html",
            chdir=doc_dir)
        os.environ['SPHINXOPTS'] = backup_sphinxopts
    else:
        shell(
            "make VENVDIR=../../venv SPHINXOPTS='{}' autobuild-dev-html".format(sphinx_opts),
            chdir=doc_dir)


def main():
    prepare_env()
    build()


if __name__ == '__main__':
    main()
