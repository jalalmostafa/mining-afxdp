#! /usr/bin/python3

import argparse
import sys
import os
from commitscommands import CommitsStatsCmds
from driverscommands import DriversSupportCmds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='A tool to extract information about AF_XDP from the Linux Kernel')
    commands = parser.add_subparsers(help='Commands', dest='command',)

    commits_cmds = CommitsStatsCmds.commands()
    commits_cmds_help = '<%s>' % ('|'.join(commits_cmds))
    commits_cmds_parser = commands.add_parser(
        'commits', help=commits_cmds_help + '\nExtract software evolution information')

    commits_cmds_parser.add_argument(
        'mode', choices=commits_cmds, help=commits_cmds_help)

    drivers_cmds = DriversSupportCmds.commands()
    drivers_cmds_help = '<%s>' % ('|'.join(drivers_cmds))
    drivers_cmds_parser = commands.add_parser(
        'support', help=drivers_cmds_help + '\nDriver Support')
    drivers_cmds_parser.add_argument('mode', choices=drivers_cmds,
                                     help=drivers_cmds_help)
    parser.add_argument('repo', help='Linux Kernel Repository Directory',)

    args = parser.parse_args()
    if not os.path.exists('./reports'):
        os.mkdir('./reports')

    if args.command == 'support':
        DriversSupportCmds(args, ).run()
    elif args.command == 'commits':
        CommitsStatsCmds(args, ).run()
    else:
        parser.print_help()
