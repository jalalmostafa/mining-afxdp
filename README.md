# Mining AF_XDP
Mining Linux Kernel Repositories to extract knowledge about AF_XDP.
The extracted information include AF_XDP driver support and its software evolution by counting commits, total inserted and deleted lines, and lines of code.

### To-do

- [ ] Launch GitHub Pages
- [ ] Check NIC features advertised by driver
- [ ] Add Multi-buffer to driver support output

## Usage

```bash
usage: ./afxdp-miner.py [-h] {commits,support} ... repourl

A tool to extract information about AF_XDP from the Linux Kernel

positional arguments:
  {commits,support}  Commands
    commits          <core|mlx5|ice> Extract software evolution information
    support          <all> Driver Support
  repourl            Repository URL

options:
  -h, --help         show this help message and exit
```
