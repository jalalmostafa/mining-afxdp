import os
from commands import Cmds
from linuxversion import XSKPOOL_RELEASE


class DriversSupportCmds(Cmds):
    NO_DRIVERS = ['sfc/rx', 'sfc/net', 'hyperv/hyperv',]
    LINUX_VIRT_DRIVERS = ['veth', 'virtio',
                          'xen-netfront', 'tun', 'bonding', 'netdevsim']

    def __init__(self, args, ) -> None:
        super().__init__(args, release=XSKPOOL_RELEASE)
        self.search_path = f'{self.repo_url}/drivers/net'

    def _parse_support_output(self, output):
        def norm(st):
            return st.split('_')[0].split('-')[0].replace('.c', '').replace('.h', '')

        lines = output.splitlines()
        drivers = []
        for line in lines:
            if not line:
                continue
            driver_path = os.path.abspath(line.split(':')[0])
            driver_path = driver_path[driver_path.find('drivers'):]
            driver_components = driver_path.split('/')
            driver_len = len(driver_components)
            if driver_len >= 5:
                vendor_idx, driver_idx = 3, 4
            elif driver_len == 4:
                vendor_idx, driver_idx = 2, 3
            elif driver_len == 3:
                vendor_idx, driver_idx = None, 2
            else:
                print('Skipping', line, len(driver_components))
                continue

            vendor = driver_components[vendor_idx] if vendor_idx else 'linux'
            driver_name = norm(driver_components[driver_idx])
            driver_name = driver_name if driver_name not in (
                'bond', 'netdevsim') else vendor
            vendor = vendor if vendor not in DriversSupportCmds.LINUX_VIRT_DRIVERS else 'linux'
            driver = f'{vendor}/{driver_name}'
            if driver not in drivers and driver not in DriversSupportCmds.NO_DRIVERS:
                drivers.append(driver)
        return list(set(drivers))

    def _zcopy_support(self,):
        cmd = ['grep', '-R', 'XDP_SETUP_XSK_POOL', self.search_path]
        output = self._run_command(cmd)
        if output is None:
            return []
        return self._parse_support_output(output)

    def _copy_support(self,):
        cmd = ['grep', '-R', 'xdp_rxq_info\|.ndo_xdp_xmit', self.search_path]
        output = self._run_command(cmd)
        if output is None:
            return []
        return self._parse_support_output(output)

    def _needwakeup_support_rx(self):
        cmd = ['grep', '-R', 'xsk_set_rx_need_wakeup', self.search_path]
        output = self._run_command(cmd)
        if output is None:
            return []
        return self._parse_support_output(output)

    def _needwakeup_support_tx(self):
        cmd = ['grep', '-R', 'xsk_set_tx_need_wakeup', self.search_path]
        output = self._run_command(cmd)
        if output is None:
            return []
        return self._parse_support_output(output)

    @Cmds.command
    def all(self):
        def _mode(driver, zc, c):
            if driver in zc and driver in c:
                return 'ZC/C'

            if driver in zc:
                return 'ZC'

            if driver in c:
                return 'C'

        def _needwakeup(driver, rx_nwf, tx_nwf):
            if driver in rx_nwf and driver in tx_nwf:
                return 'Yes'

            if driver in rx_nwf:
                return 'Only RX'

            if driver in tx_nwf:
                return 'Only TX'

            return 'No'

        self.file.addHeader(level=2, text='Drivers Support')
        data = {}
        for ver in self.versions:
            tag = ver.git_tag
            print(f'Checking out tag: \'{tag}\'')
            self.git.checkout(tag)

            table = []
            copy_drivers = self._copy_support()
            zcopy_drivers = self._zcopy_support()
            needwakeup_flag_rx = self._needwakeup_support_rx()
            needwakeup_flag_tx = self._needwakeup_support_tx()
            all_drivers = set(copy_drivers + zcopy_drivers +
                              needwakeup_flag_rx + needwakeup_flag_tx)
            for driver in all_drivers:
                mode = _mode(driver, zcopy_drivers, copy_drivers)
                needwakeup_flag = _needwakeup(
                    driver, needwakeup_flag_rx, needwakeup_flag_tx)
                row = {'Driver': driver, 'Mode': mode,
                       'Need Wake-Up': needwakeup_flag}
                table.append(row)
            data[tag] = sorted(table, key=lambda x: x['Driver'])

        for tag, table in reversed(data.items()):
            self.file.addHeader(level=3, text=tag)
            self.file.writeTextLine('<details>', html_escape=False)
            zc_len = len(list(filter(lambda x: x['Mode'] == 'ZC/C', table)))
            self.file.writeTextLine(
                f'<summary>Total: {len(table)} - Zero Copy: {zc_len}</summary>', html_escape=False)
            self.file.addTable(dictionary_list=table)
            self.file.writeTextLine('</details>', html_escape=False)
