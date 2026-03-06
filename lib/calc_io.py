#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import multiprocessing
import platform
from lib.log_cat import LogCat
from lib.version import VERSION

log = LogCat()

class calcIO():

    def get(self):
        return self.__calculate_best_io_threads()

    def __get_system_dynamic_port_range(self):
        system = platform.system()
        try:
            if system == "Windows":
                import winreg
                reg_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    try:
                        min_port, _ = winreg.QueryValueEx(key, "TCPStartPort")
                    except FileNotFoundError:
                        min_port = 49152 
                    try:
                        max_port, _ = winreg.QueryValueEx(key, "TCPEndPort")
                    except FileNotFoundError:
                        max_port = 65535 
                return (min_port, max_port)
            
            elif system == "Linux":
                with open("/proc/sys/net/ipv4/ip_local_port_range", "r") as f:
                    port_range = f.read().strip().split()
                    min_port = int(port_range[0])
                    max_port = int(port_range[1])
                return (min_port, max_port)
            
            elif system == "Darwin":
                import subprocess
                start_port = subprocess.check_output(
                    ["sysctl", "-n", "net.inet.ip.portrange.first"],
                    text=True
                ).strip()
                end_port = subprocess.check_output(
                    ["sysctl", "-n", "net.inet.ip.portrange.last"],
                    text=True
                ).strip()
                min_port = int(start_port)
                max_port = int(end_port)
                return (min_port, max_port)
            
            else:
                return (1024, 65535)
        except Exception as e:
            log.error(f"Failed to obtain system port range: {e}, using default port range (1024, 65535)")
            return (1024, 65535)

    def __calculate_best_io_threads(self,
        cpu_core_multiplier: int = 5,
        max_threads_limit: int = 100
    ) -> int:
        cpu_logical_cores = multiprocessing.cpu_count()
        cpu_based_threads = cpu_logical_cores * cpu_core_multiplier
        min_port, max_port = self.__get_system_dynamic_port_range()
        available_ports = max_port - min_port
        port_based_threads = int(available_ports / 2)  
        best_threads = min(cpu_based_threads, max_threads_limit, port_based_threads)
        return best_threads

 