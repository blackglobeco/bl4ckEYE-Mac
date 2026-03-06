#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import os
import re
import json
import sys
import threading
import signal
from http.server import HTTPServer, SimpleHTTPRequestHandler
from lib.version import VERSION
from lib.camlib import *
from lib.log_cat import *
from lib.play import Player

LOGO = "\033[38;5;208m"+r'''
  ,-.       _,---._ __  / \
 /  )    .-'       `./ /   \
(  (   ,'            `/    /|
 \  `-"             \'\   / |
  `.              ,  \ \ /  |
   /`.          ,'-`----Y   |
  (            ;        |   '
  |  ,-.    ,-'         |  /
  |  | (   |            | /
  )  |  \  `.___________|/
  `--'   `--'
[Maptnh@S-H4CK13]      [Blood Cat Map Terminal '''+VERSION+r''']    [https://github.com/MartinxMax]'''+"\033[0m"

CONFIG_PATH = os.path.join('.', 'data', 'bloodcatmap.conf')
SLOT_COUNT = 10
API_PORT = 34713
HTTP_HOST = "0.0.0.0"

cam = CamLib()

class GlobalBCHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join('.', 'data'), **kwargs)

    def do_GET(self):
        if self.path.strip("/") != "global.bc":
            self.send_error(403, "Forbidden")
            return
        return super().do_GET()
    
    def log_message(self, format, *args):
        return

def start_http_server():
    def get_local_ip():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    try:
        server_address = (HTTP_HOST, API_PORT)
        httpd = HTTPServer(server_address, GlobalBCHandler)
        local_ip = get_local_ip()
        print(f"[+] Local HTTP server started:")
        print(f"    - Local access: http://127.0.0.1:{API_PORT}/global.bc")
        print(f"    - LAN access: http://{local_ip}:{API_PORT}/global.bc")
        httpd.serve_forever()
    except Exception as e:
        print(f"\n[!] Failed to start HTTP server: {e}")
        print(f"    - Port {API_PORT} may be in use")

class RTSPConsole:
    def __init__(self):
        self.local_data = []
        self.remote_data = {}
        self.all_data = []
        self.filtered = []
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)
        self.load_all_data()

    def load_all_data(self):
        # self._load_local_data()
        self._load_remote_data()
        self._merge_data()
        self.filtered = self.all_data.copy()
        print(f"[+] Loaded total {len(self.all_data)} entries")
 

    # def _load_local_data(self):
    #     self.local_data = []
    #     DATA_PATH = "./data/rtsp.json"
    #     if not os.path.exists(DATA_PATH):
    #         print(f"[!] Local data file not found: {DATA_PATH}")
    #         return
    #     try:
    #         with open(DATA_PATH, "r", encoding="utf-8") as f:
    #             raw_data = json.load(f)
    #             if isinstance(raw_data, list):
    #                 self.local_data = [
    #                     {
    #                         "rtsp": item.get("rtsp", ""),
    #                         "lalo": item.get("lalo", ""),
    #                         "sys_org": item.get("sys_org", ""),
    #                         "asn": item.get("asn", ""),
    #                         "network": item.get("network", ""),
    #                         "source": "local"
    #                     }
    #                     for item in raw_data
    #                     if isinstance(item, dict) and item.get("rtsp")
    #                 ]
    #     except Exception as e:
    #         print(f"[!] Failed to load local data: {e}")
    #         self.local_data = []

    def _load_remote_data(self):
        self.remote_data = {}
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                remote_urls = json.load(f)
                if not isinstance(remote_urls, list):
                    remote_urls = []
            for idx, url in enumerate(remote_urls):
                try:
                    remote_raw = cam.get_DB_data(url.strip())
                    if not remote_raw:
                        print(f"[!] Empty data from remote URL: {url}")
                        continue
                    parsed_data = self._parse_raw_to_dict(remote_raw, url, idx)
                    self.remote_data.update(parsed_data)
                except Exception as e:
                    print(f"[!] Failed to load remote URL ({idx+1}): {url} - {e}")
                    continue
        except Exception as e:
            print(f"[!] Failed to load remote config: {e}")

    def _parse_raw_to_dict(self, raw, source_url, idx):
        result = {}
        if not raw:
            return result

        def process_obj(obj):
            try:
                rtsp = obj.get("rtsp", "") if isinstance(obj, dict) else ""
                data_obj = obj.get("data", {}) if isinstance(obj, dict) else {}
                lalo = data_obj.get("lalo", "")
                sys_org = data_obj.get("sys_org", "")
                asn = data_obj.get("asn", "")
                network = data_obj.get("network", "")
                ip_match = re.search(r'@([\d\.]+):?', rtsp)
                if ip_match and rtsp:
                    ip = ip_match.group(1)
                    result[ip] = {
                        "rtsp": rtsp,
                        "lalo": lalo,
                        "sys_org": sys_org,
                        "asn": asn,
                        "network": network,
                        "source": "remote"
                    }
            except Exception as e:
                print(f"[!] Parse object error: {e}")
                return

        if isinstance(raw, str):
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        process_obj(obj)
                except Exception:
                    continue
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    process_obj(item)
                else:
                    try:
                        obj = json.loads(item)
                        if isinstance(obj, dict):
                            process_obj(obj)
                    except Exception:
                        continue
        elif isinstance(raw, dict):
            process_obj(raw)

        return result

    def _merge_data(self):
        remote_list = list(self.remote_data.values())
        merged = self.local_data.copy()
        local_ips = set()
        for item in self.local_data:
            ip = self.extract_ip(item.get("rtsp", ""))
            if ip != "N/A":
                local_ips.add(ip)
        for remote_item in remote_list:
            remote_ip = self.extract_ip(remote_item.get("rtsp", ""))
            if remote_ip not in local_ips and remote_ip != "N/A":
                merged.append(remote_item)
        self.all_data = []
        for global_id, item in enumerate(merged, 1):
            self.all_data.append({
                "global_id": global_id,
                **item
            })

    def show_help(self):
        help_text = """
=== BloodCat Map Terminal - Help Manual ===
Commands:
  help                - Show this help message
  show                - Show all entries with detailed fields (global ID)
  show brief          - Show brief list (global ID, IP, Source)
  search <keyword>    - Search entries (supports: IP, RTSP, ASN, sys_org, network)
  play <global_id>    - Play RTSP stream by GLOBAL ID
  info <global_id>    - Show detailed information by GLOBAL ID
  reload              - Reload all data (local + remote)
  reset               - Reset filter to show all entries
  add <url>           - Add remote DB URL to config
  remove <url>        - Remove remote DB URL from config
  urls                - List all configured remote URLs
  exit/quit           - Exit the console
"""
        print(help_text)

    def show(self, mode="detailed"):
        if not self.filtered:
            print("[!] No data to show")
            return
        if mode == "brief":
            print("\nGLOBAL ID   IP              Source")
            print("-" * 45)
            for item in self.filtered:
                global_id = item.get("global_id", "N/A")
                ip = self.extract_ip(item.get("rtsp", ""))
                source = item.get("source", "unknown")
                print(f"{global_id:<9} {ip:<15} {source}")
            print(f"\nTotal entries: {len(self.filtered)}")
        else:
            print("\n=== All Entries (Detailed) ===")
            for item in self.filtered:
                global_id = item.get("global_id", "N/A")
                ip = self.extract_ip(item.get("rtsp", ""))
                print(f"\n[Global ID: {global_id}] IP: {ip}")
                print(f"  RTSP:    {item.get('rtsp', 'N/A')}")
                print(f"  Lalo:    {item.get('lalo', 'N/A')}")
                print(f"  ASN:     {item.get('asn', 'N/A')}")
                print(f"  Sys_Org: {item.get('sys_org', 'N/A')}")
                print(f"  Network: {item.get('network', 'N/A')}")
                print(f"  Source:  {item.get('source', 'N/A')}")
            print(f"\nTotal entries: {len(self.filtered)}")

    def reset_filter(self):
        self.filtered = self.all_data.copy()
        print(f"[+] Filter reset to all entries (total: {len(self.filtered)})")

    def show_info(self, target_id):
        try:
            target_id = int(target_id)
            target_item = next((item for item in self.all_data if item.get("global_id") == target_id), None)
            if not target_item:
                print(f"[!] Global ID {target_id} not found")
                return
            ip = self.extract_ip(target_item.get("rtsp", ""))
            print(f"\n=== Detailed Info for Global ID {target_id} (IP: {ip}) ===")
            print(f"RTSP:    {target_item.get('rtsp', 'N/A')}")
            print(f"Lalo:    {target_item.get('lalo', 'N/A')}")
            print(f"ASN:     {target_item.get('asn', 'N/A')}")
            print(f"Sys_Org: {target_item.get('sys_org', 'N/A')}")
            print(f"Network: {target_item.get('network', 'N/A')}")
            print(f"Source:  {target_item.get('source', 'N/A')}")
            print()
        except ValueError:
            print("[!] Invalid ID (must be a number)")
        except Exception as e:
            print(f"[!] Error showing info: {e}")

    def search(self, keyword):
        keyword = keyword.lower()
        result = []
        for item in self.all_data:
            search_text = (
                f"{item.get('rtsp', '')} {item.get('lalo', '')} "
                f"{item.get('sys_org', '')} {item.get('asn', '')} "
                f"{item.get('network', '')} {item.get('source', '')} "
                f"{self.extract_ip(item.get('rtsp', ''))}"
            ).lower()
            if keyword in search_text:
                result.append(item)
        self.filtered = result
        print(f"[+] Found {len(result)} matches")
        if len(result) > 0:
            self.show(mode="brief")

    def play(self, target_id):
        try:
            target_id = int(target_id)
            target_item = next((item for item in self.all_data if item.get("global_id") == target_id), None)
            if not target_item:
                print(f"[!] Global ID {target_id} not found")
                return
            url = target_item.get("rtsp", "")
            ip = self.extract_ip(url)
            source = target_item.get("source", "unknown")
            global_id = target_item.get("global_id", "N/A")
            print(f"[+] Playing Global ID {global_id} - {ip} (Source: {source})")
            print("[*] Press Ctrl+C to stop\n")
            player = Player()
            try:
                player.play(rtsp=url, title=f"{ip}_{source}_ID{global_id}", mode="ascii")
            except KeyboardInterrupt:
                self.clear_screen()
        except ValueError:
            print("[!] Invalid ID (must be a number)")
        except Exception as e:
            print(f"[!] Error playing stream: {e}")

    def add_remote_url(self, url):
        url = url.strip()
        if not url:
            print("[!] Empty URL")
            return
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                urls = json.load(f)
                if not isinstance(urls, list):
                    urls = []
            if url in urls:
                print("[!] URL already exists")
                return
            urls.append(url)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            print(f"[+] Added remote URL: {url}")
            self.load_all_data()
        except Exception as e:
            print(f"[!] Failed to add URL: {e}")

    def remove_remote_url(self, url):
        url = url.strip()
        if not url:
            print("[!] Empty URL")
            return
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                urls = json.load(f)
                if not isinstance(urls, list):
                    urls = []
            if url not in urls:
                print("[!] URL not found")
                return
            urls = [u for u in urls if u != url]
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            print(f"[+] Removed remote URL: {url}")
            self.load_all_data()
        except Exception as e:
            print(f"[!] Failed to remove URL: {e}")

    def list_remote_urls(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                urls = json.load(f)
                if not isinstance(urls, list):
                    urls = []
            print("\nRemote URLs:")
            print("-" * 50)
            if not urls:
                print("  (empty)")
            else:
                for idx, url in enumerate(urls, 1):
                    print(f"{idx}. {url}")
            print()
        except Exception as e:
            print(f"[!] Failed to list URLs: {e}")

    def extract_ip(self, url):
        match = re.search(r'@([\d\.]+):', url)
        return match.group(1) if match else "N/A"

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def repl(self):
        while True:
            try:
                cmd = input("BloodCatMap-Terminal# ").strip()
            except KeyboardInterrupt:
                self.clear_screen()
                print("\nexit")
                break
            if not cmd:
                continue
            args = cmd.split()
            base_cmd = args[0].lower()
            if base_cmd in ("exit", "quit"):
                break
            elif base_cmd == "help":
                self.show_help()
            elif base_cmd == "show":
                if len(args) > 1 and args[1].lower() == "brief":
                    self.show(mode="brief")
                else:
                    self.show(mode="detailed")
            elif base_cmd == "reset":
                self.reset_filter()
            elif base_cmd == "info" and len(args) == 2:
                self.show_info(args[1])
            elif base_cmd == "search" and len(args) > 1:
                self.search(" ".join(args[1:]))
            elif base_cmd == "play" and len(args) == 2:
                self.play(args[1])
            elif base_cmd == "reload":
                print("[+] Reloading data...")
                self.load_all_data()
            elif base_cmd == "add" and len(args) > 1:
                self.add_remote_url(" ".join(args[1:]))
            elif base_cmd == "remove" and len(args) > 1:
                self.remove_remote_url(" ".join(args[1:]))
            elif base_cmd == "urls":
                self.list_remote_urls()
            else:
                print(f"[!] Unknown command: {base_cmd}")
                print("    Type 'help' to see available commands")

def signal_handler(sig, frame):
    os.system("cls" if os.name == "nt" else "clear")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    print(LOGO)
    print("Type 'help' to see available commands")
    print("-" * 50)
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    console = RTSPConsole()
    console.repl()