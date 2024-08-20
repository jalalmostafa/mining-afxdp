import subprocess
import os
import datetime as dt
from pydriller import Git
from linuxversion import LinuxVersion, INIT_RELEASE
from markdowngenerator import MarkdownGenerator


class Cmds:
    def __init__(self, args, release=INIT_RELEASE) -> None:
        self.ns = args
        self.repo_url = os.path.abspath(args.repo)
        self.git = Git(self.repo_url)
        self.versions = []
        for tag in self.git.repo.tags:
            if 'dontuse' not in tag.name and 'rc' not in tag.name \
                    and LinuxVersion(tag.name,) >= release:
                year = tag.commit.committed_datetime.year
                self.versions.append(LinuxVersion(tag.name, year=year))
        self.versions.sort()
        report_date = dt.datetime.today().strftime('%y%m%d-%H%M')
        self.file = MarkdownGenerator(filename=f'./reports/{self.git.project_name}-{report_date}.md',
                                      enable_write=False,).__enter__()
        self.file.addHeader(level=1, text=f'Report - {report_date}')
        self.file.genTableOfContent(linenumber=3)

    def run(self):
        cmd = self.ns.mode
        if not hasattr(self, cmd):
            print(f'Command \'({cmd})\' not found')
            return
        return getattr(self, cmd)()

    def _run_command(self, cmd):
        process = subprocess.run(cmd, capture_output=True, text=True)
        return process.stdout or None

    def __del__(self):
        if self.file:
            self.file.__exit__()

    def command(cmd):
        cmd.__decorated__ = True
        return cmd

    @classmethod
    def commands(cls):
        return [k for k, v in cls.__dict__.items() if hasattr(v, '__decorated__')]
