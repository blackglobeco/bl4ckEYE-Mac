#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝

import socket
import base64
import argparse
import json
from lib.camlib import * 
from lib.fofaget import * 
from lib.log_cat import * 
from lib.version import VERSION

log = LogCat()
cam = CamLib()

LOGO = "\033[31m"+r'''

                  ;,_            ,
                 _uP~"b          d"u,
                dP'   "b       ,d"  "o
               d"    , `b     d"'    "b
              l] [    " `l,  d"       lb
              Ol ?     "  "b`"=uoqo,_  "l
            ,dBb "b        "b,    `"~~TObup,_
          ,d" (db.`"         ""     "tbc,_ `~"Yuu,_
        .d" l`T'  '=                      ~     `""Yu,
      ,dO` gP,                           `u,   b,_  "b7
     d?' ,d" l,                           `"b,_ `~b  "1
   ,8i' dl   `l                 ,ggQOV",dbgq,._"  `l  lb
  .df' (O,    "             ,ggQY"~  , @@@@@d"bd~  `b "1
 .df'   `"           -=@QgpOY""     (b  @@@@P db    `Lp"b,
.d(                  _               "ko "=d_,Q`  ,_  "  "b,
Ql         .         `"qo,._          "tQo,_`""bo ;tb,    `"b,
qQ         |L           ~"QQQgggc,_.,dObc,opooO  `"~~";.   __,7,
qp         t\io,_           `~"TOOggQV""""        _,dg,_ =PIQHib.
`qp        `Q["tQQQo,_                          ,pl{QOP"'   7AFR`
  `         `tb  '""tQQQg,_             p" "b   `       .;-.`Vl'
             "Yb      `"tQOOo,__    _,edb    ` .__   /`/'|  |b;=;.__
                           `"tQQQOOOOP""`"\QV;qQObob"`-._`\_~~-._
                                """"    ._        /   | |oP"\_   ~\ ~\_~\
                                        `~"\ic,qggddOOP"|  |  ~\   `\~-._
                                          ,qP`"""|"   | `\ `;   `\   `\
                               _        _,p"     |    |   `\`;    |    |
                                "boo,._dP"       `\_  `\    `\|   `\   ;
                                 `"7tY~'            `\  `\    `|_   |
                                                      `~\  |'''+'\033[0m'+'\033[35m'+r'''
[Maptnh@S-H4CK13]      [Blood Cat '''+VERSION+r''']    [https://github.com/MartinxMax]'''+'\033[0m'

    
def read_ips(filename: str):
    ips = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                ip_port = line.strip()
                if not ip_port:
                    continue
                if ':' in ip_port:
                    ip_part, port_part = ip_port.split(':', 1)
                    if not port_part.isdigit():
                        log.error(f"Line {line_num} format error (port is not a number): {ip_port}, skipped")
                        continue
                ips.append(ip_port)
        if not ips:
            log.error(f"No valid IP/IP:PORT found in file {filename}")
        return ips
    
    except FileNotFoundError:
        log.error(f"File {filename} does not exist!")
        sys.exit(1)
    except Exception as e:
        log.error(f"Failed to read file {filename}: {str(e)}")
        sys.exit(1)




def read_and_exe_hik_credentials(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cred_list = json.load(f)
        
        if not isinstance(cred_list, list):
            log.error(f"{file_path} Format error: Root node is not a list!")
            return

        log.info(f"Preparing to test Hikvision camera information in {file_path} (total {len(cred_list)} entries)")
        
        for index, device in enumerate(cred_list, 1):
            ip = device.get('IP')
            rtsp_port = device.get('RTSP_PORT')
            password = device.get('PASSWORD')
            cam.hiv(ip, rtsp_port, password)
    except FileNotFoundError:
        log.error(f"File {file_path} does not exist, please check the path!")
    except json.JSONDecodeError:
        log.error(f"{file_path} is not a valid JSON format, please check the file content!")
    except Exception as e:
        log.error(f"An unknown error occurred while processing the file: {str(e)}")
 

def main():
    print(LOGO)
    parser = argparse.ArgumentParser(description='Blood Cat - RTSP Camera Weak Credential Scanner')
    parser.add_argument('--country', default='', type=str, help='Country')
    parser.add_argument('--city', default='', type=str, help='City')
    parser.add_argument('--region', default='', type=str, help='Area')
    parser.add_argument('--key',  default='', type=str, help='Fofa API key')
    parser.add_argument('--ip', default='', type=str, help='IP:PORT')
    parser.add_argument('--ips', default='', type=str, help='Targets list file (each line: IP or IP:PORT)')
    parser.add_argument('--password', default='', type=str, help='Password Spraying')
    parser.add_argument('--merge', action='store_true', help='Merge and update all data in ./data into a single BC file')
    parser.add_argument('--hiv', default='', help='Load Hikvision credentials file')
    parser.add_argument('--live', default='', help='Filter currently active cameras in the BC file')
    args = parser.parse_args()
    if args.live:
        cam.ping_live(args.live)
        sys.exit(0)
    if args.hiv:
        read_and_exe_hik_credentials(args.hiv)
        sys.exit(0)
    if args.merge:
        cam.merge_all_bc()
    else:
        # ---------- IPS Module ----------
        if args.ips:
            log.info(f"Loaded ips file: [{args.ips}]")
            ips_list = read_ips(args.ips)

            if not ips_list:
                sys.exit(0)

            real = cam.filter_ips(ips_list)
            for ip_ in real:
                try:
                    ip = ip_.split(':')[0]
                    port = int(ip_.split(':')[-1]) if ':' in ip_ else 554
                    cam.run(ip, port, args.password)
                except Exception:
                    log.error("Invalid format")

        # ---------- FOFA Module ----------
        elif args.key:
            fofa = Fofa()
            info = fofa.query(
                key=args.key,
                city=args.city,
                country=args.country,
                region=args.region
            )

            if info:
                real = cam.filter_ips(info)
                for i in real:
                    ip = i.split(':')[0]
                    port = int(i.split(':')[-1])
                    cam.run(ip, port, args.password)

        # ---------- Single IP Module ----------
        elif args.ip:
            if ':' not in args.ip:
                log.error("Invalid format")
                sys.exit(0)

            cam.run(
                args.ip.split(':')[0],
                int(args.ip.split(':')[-1]),
                args.password
            )

        # ---------- Help ----------
        else:
            parser.print_help()


if __name__ == '__main__':
    main() 

