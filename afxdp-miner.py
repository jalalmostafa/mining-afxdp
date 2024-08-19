#! /usr/bin/python3

import argparse
import sys
import os
from commitscommands import CommitsStatsCmds
from driverscommands import DriversSupportCmds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    commands = parser.add_subparsers(help='Commands', dest='command',)

    commits_cmds = commands.add_parser('commits')
    commits_cmds.add_argument('mode', choices=CommitsStatsCmds.ARGUMENTS,)

    drivers_cmds = commands.add_parser('support')
    drivers_cmds.add_argument('mode', choices=DriversSupportCmds.ARGUMENTS,)

    args, unknowns = parser.parse_known_args()

    if not os.path.exists('./reports'):
        os.mkdir('./reports')

    if args.command == 'support':
        DriversSupportCmds(args, unknowns,).run()
    elif args.command == 'commits':
        CommitsStatsCmds(args, unknowns,).run()
    else:
        print('help')
