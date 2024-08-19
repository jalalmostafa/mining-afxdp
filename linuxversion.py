class LinuxVersion:

    def __init__(self, tag, year=None) -> None:
        tag_name = tag if isinstance(tag, str) else tag.name
        self.tuple = self._version_to_tuple(tag_name)
        self.major, self.minor, self.rev, self.rc = self.tuple
        self.git_tag = tag_name
        self.year = year

    def _version_to_tuple(self, version: str) -> tuple:
        try:
            if version.startswith('v'):
                version = version.removeprefix('v')

            version = version.removesuffix('-tree')

            norc_values = version.split('-rc')
            rc = int(norc_values[1]) if len(norc_values) == 2 else 1000
            version_ints = list(map(int, norc_values[0].split('.')))
            if len(version_ints) < 3:
                for _ in range(0, 3 - len(version_ints)):
                    version_ints.append(0)

            version_ints.append(rc)
            return tuple(version_ints)
        except Exception as e:
            print(version)
            raise e

    def __eq__(self, other: object) -> bool:
        return self.tuple == other.tuple

    def __ne__(self, other: object):
        return self.tuple != other.tuple

    def __lt__(self, other: object):
        return self.tuple < other.tuple

    def __le__(self, other: object):
        return self.tuple <= other.tuple

    def __gt__(self, other: object):
        return self.tuple > other.tuple

    def __ge__(self, other: object):
        return self.tuple >= other.tuple

    def __str__(self) -> str:
        return f'v{self.major}.{self.minor}.{self.rev}-rc{self.rc}' if self.rc else f'v{self.major}.{self.minor}.{self.rev}'


INIT_RELEASE_STRING = 'v4.18'
INIT_RELEASE = LinuxVersion(INIT_RELEASE_STRING)
XSKPOOL_RELEASE = LinuxVersion('v5.10')
