from commands import Cmds
from pydriller import Commit, Repository


class CommitsStatsCmds(Cmds):
    def __init__(self, args,) -> None:
        super().__init__(args,)
        self.relevant_commits = []

    def _paths_in_string(self, path, string):
        if not string:
            return False
        return string.startswith(path)

    def _loc(self, f):
        cmd = ['cloc', '--hide-rate', '--quiet',
               '--sum-one', '--md', f]
        output = self._run_command(cmd,)
        if output is None:
            return 0
        return int(output.split('\n')[-2].split('|')[-1])

    def _commit_stats(self, file, commit: Commit):
        insertions = 0
        deletions = 0

        for mfile in commit.modified_files:
            if self._paths_in_string(file, mfile.old_path) \
               or self._paths_in_string(file, mfile.new_path):
                if commit.hash not in self.relevant_commits:
                    self.relevant_commits.append(commit.hash)
                insertions += mfile.added_lines
                deletions += mfile.deleted_lines

        return insertions, deletions

    def _collective_loc(self, files):
        count = 0

        def file_filter(i):
            return any(self._paths_in_string(f'{self.repo_url}/{path}', i) for path in files)

        for f in filter(file_filter, self.git.files()):
            count += self._loc(f)
        return count

    def _stats(self, files):
        table = []
        for ver in self.versions:
            tag = ver.git_tag
            print(f'Checking out tag: \'{tag}\'')
            self.git.checkout(tag)

            insertions = 0
            deletions = 0
            for f in files:
                repo = Repository(self.repo_url, to_tag=tag,
                                  num_workers=16, filepath=f)

                for commit in repo.traverse_commits():
                    i, d = self._commit_stats(f, commit)
                    insertions += i
                    deletions += d

            loc = self._collective_loc(files)
            table.append({'Tag': tag, 'Year': ver.year,
                          'Total Commits': len(self.relevant_commits),
                          'LOC': loc, 'Insertions': insertions, 'Deletions': deletions,
                          })
        return table

    def _dump_stats(self, header, files):
        table = self._stats(files)
        self.file.addHeader(level=2, text=header)
        self.file.addTable(dictionary_list=table)

    @Cmds.command
    def core(self):
        CORE_PATHS = ['net/xdp/', 'net/core/xdp.c', 'include/net/xdp.h',
                      'include/net/xdp_priv.h', 'include/net/xdp_sock_drv.h',
                      'include/net/xsk_buff_pool.h', 'include/net/xdp_sock.h',
                      'net/core/filter.c']
        self._dump_stats('Core', CORE_PATHS)

    @Cmds.command
    def mlx5(self):
        MLX5_PATHS = ['drivers/net/ethernet/mellanox/mlx5/core/en/xsk',
                      'drivers/net/ethernet/mellanox/mlx5/core/en/xdp.c',
                      'drivers/net/ethernet/mellanox/mlx5/core/en/xdp.h']
        self._dump_stats('MLX5', MLX5_PATHS)

    @Cmds.command
    def ice(self):
        ICE_PATHS = ['drivers/net/ethernet/intel/ice/ice_xsk.c',
                     'drivers/net/ethernet/intel/ice/ice_xsk.h']
        self._dump_stats('ICE', ICE_PATHS)
