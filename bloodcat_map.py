#!/usr/bin/python3
# @Мартин.
import os
import sys
import json
import re
import time
import threading
import base64
import subprocess
import requests
import cv2

from flask import Flask, request, jsonify, Response, send_from_directory
from lib.camlib import CamLib
from lib.log_cat import LogCat
from lib.version import VERSION
from http.server import HTTPServer, SimpleHTTPRequestHandler

log = LogCat()
cam = CamLib()

CONFIG_PATH = os.path.join('.', 'data', 'bloodcatmap.conf')
SLOT_COUNT = 10
API_SER = 34713
WEB_PORT = 5000

os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)

app = Flask(__name__, static_folder='location', static_url_path='/location')

LOGO = (
    "\033[38;5;208m"
    "[Maptnh@S-H4CK13]  [Blood Cat Map " + VERSION + "]  [https://github.com/MartinxMax]"
    "\033[0m"
)


class DataLoader(threading.Thread):
    def __init__(self, remote_urls=None):
        super().__init__(daemon=True)
        self.remote_urls = remote_urls or []
        self.result = {}

    def parse_raw_to_dict(self, raw, source_label, source_url=None, icon_path=None):
        result = {}
        if not raw:
            return result

        def process_obj(obj):
            try:
                rtsp = obj.get("rtsp", "") if isinstance(obj, dict) else ""
                data_obj = obj.get("data", {}) if isinstance(obj, dict) else {}
                lalo = data_obj.get("lalo", "") if isinstance(data_obj, dict) else ""
                sys_org = data_obj.get("sys_org", "") if isinstance(data_obj, dict) else ""
                asn = data_obj.get("asn", "") if isinstance(data_obj, dict) else ""
                network = data_obj.get("network", "") if isinstance(data_obj, dict) else ""
            except Exception:
                rtsp = ""; lalo = ""; sys_org = ""; asn = ""; network = ""
            m = re.search(r'@([\d\.]+):?', rtsp)
            if m and lalo:
                ip = m.group(1)
                result[ip] = {
                    "rtsp": rtsp,
                    "lalo": lalo,
                    "sys_org": sys_org,
                    "asn": asn,
                    "network": network,
                    "source": source_label,
                    "icon": icon_path or "/location/color_1.png",
                    "source_url": source_url or ""
                }

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
        else:
            if isinstance(raw, dict):
                process_obj(raw)
        return result

    def run(self):
        remote_merged = {}
        try:
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    remote_urls = json.load(f)
                    if not isinstance(remote_urls, list):
                        remote_urls = []
            except Exception:
                remote_urls = []
            for idx, url in enumerate(remote_urls):
                try:
                    remote_raw = cam.get_DB_data(url)
                    if not remote_raw:
                        continue
                    slot_index = (idx % SLOT_COUNT) + 1
                    icon_path = f"/location/color_{slot_index}.png"
                    parsed = self.parse_raw_to_dict(remote_raw, 'remote', source_url=url, icon_path=icon_path)
                    for k, v in parsed.items():
                        remote_merged[k] = v
                except Exception as e:
                    print("Error processing remote url", url, e)
                    continue
        except Exception as e:
            print("DataLoader remote error:", e)
        self.result = remote_merged


_markers_data = {}
_data_lock = threading.Lock()


def reload_data():
    loader = DataLoader()
    loader.start()
    loader.join(timeout=30)
    with _data_lock:
        global _markers_data
        _markers_data = loader.result
    log.info(f"Data reloaded: {len(_markers_data)} markers")


class GlobalBCHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join('.', 'data'), **kwargs)

    def do_GET(self):
        if self.path.strip("/") != "global.bc":
            self.send_error(403, "Forbidden")
            return
        return super().do_GET()

    def log_message(self, format, *args):
        pass


def start_bc_server():
    server_address = ("0.0.0.0", API_SER)
    httpd = HTTPServer(server_address, GlobalBCHandler)
    log.info(f"BlackEYE local BC server running on port {API_SER}")
    httpd.serve_forever()


HTML = r'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>👁️‍🗨️ BlackEYE</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
*, *::before, *::after { box-sizing: border-box; }
html, body, #map { height: 100%; margin: 0; padding: 0; background: #000; font-family: "Segoe UI", Arial, sans-serif; }

.cursor-map { cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="24"><text x="0" y="18" font-size="18" fill="%23f44" font-weight="bold">[ ]</text></svg>') 12 12, auto !important; }
.leaflet-marker-icon { cursor: pointer !important; }
.ip-tooltip { background: rgba(0,0,0,0.78); color: #fff; font-size: 12px; padding: 6px 10px; border-radius: 6px; pointer-events: none; }

#searchBox {
    position: absolute; top: 10px; right: 10px; z-index: 9999;
    background: rgba(0,0,0,0.82); color: #fff; padding: 8px;
    border-radius: 8px; width: 310px;
    border: none;
}
#searchInput { width: 100%; padding: 5px 8px; border-radius: 4px; border: none; outline: none; background: #1a1a1a; color: #fff; }
#searchResults { max-height: 150px; overflow-y: auto; margin-top: 4px; font-size: 12px; }
.searchItem { padding: 4px 6px; cursor: pointer; border-radius: 3px; }
.searchItem:hover { background: rgba(255,50,50,0.15); }


#markerCount {
    position: absolute; top: 10px; left: 50px; z-index: 9999;
    background: rgba(0,0,0,0.75); color: #fff; padding: 5px 10px;
    border-radius: 6px; font-size: 12px; border: none;
    display: flex; align-items: center; gap: 6px;
}
#liveDotMap {
    width: 10px; height: 10px; border-radius: 50%;
    background: #f33;
    box-shadow: 0 0 6px #f33;
    animation: blink 1.2s ease-in-out infinite;
    flex-shrink: 0;
}

/* ---- Hack Box ---- */
#hackBox {
    position: absolute; right: 10px; bottom: 400px; z-index: 9999;
    background: rgba(0,0,0,0.82); color: #fff; padding: 10px;
    border-radius: 8px; width: 310px;
    border: none;
    display: flex; flex-direction: column; gap: 7px;
}
#hackTitle {
    font-size: 12px; font-weight: bold; color: #fff;
    display: flex; align-items: center; gap: 6px; letter-spacing: .5px;
}
#hackTitle::before {
    content: "👁️‍🗨️"; font-size: 13px;
}
#hackInputRow { display: flex; gap: 6px; }
#hackIpInput {
    flex: 1; padding: 5px 8px; border-radius: 4px; border: none; outline: none;
    background: #1a1a1a; color: #fff; font-size: 12px;
    border: none;
}

#hackBtn {
    padding: 5px 12px; border-radius: 4px; border: none;
    background: rgba(180,0,0,0.7); color: #f99; cursor: pointer;
    font-weight: bold; font-size: 12px; transition: background .15s;
    white-space: nowrap;
}
#hackBtn:hover { background: rgba(220,0,0,0.85); }
#hackBtn:disabled { opacity: .45; cursor: not-allowed; }
#hackStatus {
    font-size: 11px; color: #888; min-height: 14px;
    display: flex; align-items: center; gap: 5px;
}
#hackStatusDot {
    width: 8px; height: 8px; border-radius: 50%; background: #444;
    flex-shrink: 0; transition: background .3s;
}
#hackLog {
    background: #0a0a0a; border-radius: 4px; border: 1px solid rgba(255,50,50,0.12);
    padding: 6px 8px; font-size: 11px; font-family: monospace;
    color: #ccc; max-height: 160px; overflow-y: auto; white-space: pre-wrap;
    word-break: break-all; display: none;
}
#hackLog::-webkit-scrollbar { width: 4px; }
#hackLog::-webkit-scrollbar-thumb { background: rgba(255,50,50,0.3); border-radius: 2px; }
.hlog-ok  { color: #4f4; }
.hlog-err { color: #f55; }
.hlog-inf { color: #fa0; }
.hlog-dim { color: #666; }

@media (max-width: 480px) { #hackBox { width: 250px; } }

/* ---- CCTV Modal ---- */
#cctvModal {
    display: none; position: fixed; top: 0; left: 0;
    width: 100%; height: 100%; z-index: 99999;
    background: rgba(0,0,0,0.75);
    align-items: center; justify-content: center;
}
#cctvModal.open { display: flex; }

#cctvModalBox {
    background: #0d0d0d;
    border: 1px solid #171717;
    border-radius: 10px;
    width: 520px; max-width: 96vw;
    box-shadow: none;
    overflow: hidden;
    display: flex; flex-direction: column;
}

#cctvModalHeader {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 14px;
    background: #0d0d0d;
    border-bottom: none;
    flex-shrink: 0;
}
#cctvModalTitle { color: #fff; font-size: 14px; font-weight: bold; flex: 1; }
#liveBadge {
    display: none; align-items: center; gap: 4px;
    font-size: 10px; color: #fff; background: rgba(255,50,50,0.12);
    border: 1px solid rgba(255,50,50,0.3); border-radius: 10px;
    padding: 2px 8px;
}
#liveDot {
    width: 7px; height: 7px; border-radius: 50%; background: #f44;
    animation: blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

#cctvModalClose {
    background: transparent; border: none; color: #aaa;
    font-size: 20px; cursor: pointer; line-height: 1; padding: 0 2px;
}
#cctvModalClose:hover { color: #fff; }

/* Tab bar */
#tabBar {
    display: flex; border-bottom: 1px solid rgba(255,50,50,0.1);
    flex-shrink: 0;
}
.tab {
    flex: 1; padding: 8px; text-align: center; font-size: 12px;
    color: #555; cursor: pointer; border: none;
    background: transparent; transition: all .15s;
}
.tab:hover { color: #f44; background: rgba(255,50,50,0.04); }
.tab.active { color: #f44; border-bottom: 2px solid #f44; background: rgba(255,50,50,0.06); }

/* Preview area */
#cctvPreviewArea {
    background: #000; width: 100%; height: 270px;
    display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden; flex-shrink: 0;
}
#cctvStreamImg {
    width: 100%; height: 100%; object-fit: contain;
    display: none;
}
#cctvSnapshotImg {
    max-width: 100%; max-height: 100%; object-fit: contain;
    display: none;
}
#previewMsg {
    color: #444; font-size: 13px; text-align: center;
    padding: 16px; line-height: 1.7; display: flex;
    flex-direction: column; align-items: center; gap: 6px;
}
#previewMsg .icon { font-size: 30px; }

#previewSpinner {
    display: none; flex-direction: column; align-items: center; gap: 10px;
    color: #aaa; font-size: 12px;
}
.spinner-ring {
    width: 36px; height: 36px;
    border: 3px solid #777;
    border-top-color: #aaa;
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Action buttons */
#previewActions {
    display: flex; gap: 8px; padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
}
.actionBtn {
    flex: 1; padding: 7px; border-radius: 5px; border: none;
    font-size: 12px; cursor: pointer; font-weight: bold; transition: all .15s;
}
#btnLive { background: rgba(255,50,50,0.1); color: #fff; border: 1px solid rgba(255,50,50,0.25); }
#btnLive:hover { background: rgba(255,50,50,0.2); }
#btnLive.streaming { background: rgba(255,60,60,0.1); color: #fff; border-color: rgba(255,60,60,0.3); }

/* Info table */
#cctvInfoTable {
    padding: 10px 14px; font-size: 12px; color: #ccc;
    border-bottom: 1px solid rgba(255,255,255,0.05); flex-shrink: 0;
}
#cctvInfoTable table { width: 100%; border-collapse: collapse; }
#cctvInfoTable td { padding: 3px 6px; }
#cctvInfoTable td:first-child { color: #ccc; width: 76px; }

@media (max-width: 480px) {
    #searchBox { width: 175px; }
    #cctvModalBox { width: 99vw; }
    #cctvPreviewArea { height: 200px; }
}
</style>
</head>
<body>

<div id="map" class="cursor-map"></div>
<div id="markerCount"><span id="liveDotMap"></span>Live Cameras: <span id="camCount">0</span></div>

<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / ASN / Network / Org"/>
    <div id="searchResults"></div>
</div>

<div id="hackBox">
    <div id="hackTitle">BlackEYE Camera Hack</div>
    <div id="hackInputRow">
        <input id="hackIpInput" placeholder="IP:PORT  e.g. 188.134.80.244:554"/>
        <button id="hackBtn">Hack</button>
    </div>
    <div id="hackStatus"><span id="hackStatusDot"></span><span id="hackStatusTxt">Ready</span></div>
    <div id="hackLog"></div>
</div>

<!-- CCTV Modal -->
<div id="cctvModal">
    <div id="cctvModalBox">

        <div id="cctvModalHeader">
            <span id="cctvModalTitle">CCTV Camera</span>
            <span id="liveBadge"><span id="liveDot"></span>LIVE</span>
            <button id="cctvModalClose" title="Close">&times;</button>
        </div>

        <div id="previewActions">
            <button class="actionBtn" id="btnLive">&#9654; Live Stream</button>
        </div>

        <div id="cctvPreviewArea">
            <img id="cctvStreamImg" alt="Live stream"/>
            <div id="previewSpinner">
                <div class="spinner-ring"></div>
                <span id="spinnerMsg">Connecting...</span>
            </div>
            <div id="previewMsg">
                <span>Click <b style="color:#aaa">Live Stream</b> to watch the camera<br>or <b style="color:#aaa">Snapshot</b> for a still frame</span>
            </div>
        </div>

        <div id="cctvInfoTable">
            <table>
                <tr><td>IP</td><td id="info_ip">-</td></tr>
                <tr><td>Org</td><td id="info_org">-</td></tr>
                <tr><td>ASN</td><td id="info_asn">-</td></tr>
                <tr><td>Network</td><td id="info_net">-</td></tr>
                <tr><td>Source</td><td id="info_src">-</td></tr>
            </table>
        </div>

    </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map', {
    minZoom: 2,
    maxBounds: [[-85.06, -180], [85.06, 180]],
    maxBoundsViscosity: 1.0
}).setView([20, 10], 2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd', maxZoom: 19
}).addTo(map);

let markers = {}, dataStore = {};
const iconCache = {};

function makeIcon(path) {
    if (!path) return makeDefaultIcon();
    if (iconCache[path]) return iconCache[path];
    try {
        const ic = L.icon({ iconUrl: path, iconSize: [28,28], iconAnchor:[14,28], popupAnchor:[0,-30] });
        iconCache[path] = ic; return ic;
    } catch(e) { return makeDefaultIcon(); }
}
function makeDefaultIcon() {
    if (iconCache['__d']) return iconCache['__d'];
    const ic = L.divIcon({
        html: '<div style="width:16px;height:16px;background:#f44;border-radius:50%;border:2px solid #900;box-shadow:0 0 8px #f44"></div>',
        className:'', iconSize:[16,16], iconAnchor:[8,8]
    });
    iconCache['__d'] = ic; return ic;
}

// ========= Modal state =========
let currentRtsp = null;
let streamActive = false;

const modal       = document.getElementById('cctvModal');
const streamImg   = document.getElementById('cctvStreamImg');
const previewMsg  = document.getElementById('previewMsg');
const spinner     = document.getElementById('previewSpinner');
const spinnerMsg  = document.getElementById('spinnerMsg');
const liveBadge   = document.getElementById('liveBadge');
const btnLive     = document.getElementById('btnLive');

function showSpinner(msg) {
    streamImg.style.display  = 'none';
    previewMsg.style.display = 'none';
    spinner.style.display    = 'flex';
    spinnerMsg.textContent   = msg || 'Connecting...';
}
function showMsg(html) {
    streamImg.style.display  = 'none';
    spinner.style.display    = 'none';
    previewMsg.style.display = 'flex';
    previewMsg.innerHTML     = html;
}
function showStream() {
    previewMsg.style.display = 'none';
    spinner.style.display    = 'none';
    streamImg.style.display  = 'block';
}

function stopStream() {
    streamActive = false;
    streamImg.src = '';
    streamImg.style.display = 'none';
    liveBadge.style.display = 'none';
    btnLive.textContent = '\u25B6 Live Stream';
    btnLive.classList.remove('streaming');
}

function startLiveStream() {
    if (!currentRtsp) return;
    if (streamActive) { stopStream(); showMsg('<span>Stream stopped</span>'); return; }

    showSpinner('Connecting to camera...');
    streamActive = true;
    btnLive.textContent = '\u25A0 Stop Stream';
    btnLive.classList.add('streaming');

    const encoded = btoa(currentRtsp);
    const src = `/api/stream?rtsp=${encodeURIComponent(encoded)}&t=${Date.now()}`;

    streamImg.onload = null;
    streamImg.onerror = null;

    // For MJPEG the image starts receiving data — we detect "first frame" via a timeout
    let firstFrameTimeout = setTimeout(() => {
        if (streamActive) showStream();
        liveBadge.style.display = 'flex';
    }, 1500);

    streamImg.onerror = () => {
        clearTimeout(firstFrameTimeout);
        stopStream();
        showMsg(
            '<span>Could not connect to camera stream.<br>' +
            '<small style="color:#555">Camera may be offline or RTSP auth failed. Try again.</small></span>'
        );
    };

    streamImg.src = src;
    // Show spinner immediately; onerror fires if stream totally fails
}


function openCctvModal(ip, item) {
    currentRtsp = item.rtsp || null;

    document.getElementById('cctvModalTitle').textContent = 'CCTV \u2014 ' + ip;
    document.getElementById('info_ip').textContent  = ip;
    document.getElementById('info_org').textContent = item.sys_org || '-';
    document.getElementById('info_asn').textContent = item.asn || '-';
    document.getElementById('info_net').textContent = item.network || '-';
    const src = item.source_url || item.source || '-';
    document.getElementById('info_src').textContent = src.length > 42 ? src.slice(0,40)+'...' : src;
    stopStream();
    showMsg(
        '<span>Click <b style="color:aaa">\u25B6 Live Stream</b> to watch</span>'
    );
    modal.classList.add('open');
}

btnLive.onclick = startLiveStream;

document.getElementById('cctvModalClose').onclick = () => {
    stopStream();
    modal.classList.remove('open');
    currentRtsp = null;
};
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        stopStream();
        modal.classList.remove('open');
        currentRtsp = null;
    }
});

// ========= Markers =========
function updateMarkers(data_obj) {
    dataStore = data_obj || {};
    const ips = new Set(Object.keys(dataStore));
    for (let ip in markers) {
        if (!ips.has(ip)) { map.removeLayer(markers[ip]); delete markers[ip]; }
    }
    for (let ip in dataStore) {
        const item = dataStore[ip];
        const parts = ('' + item.lalo).split(',').map(x => parseFloat(x));
        if (parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) continue;
        const coords = [parts[0], parts[1]];
        const icon = makeIcon(item.icon);
        if (markers[ip]) {
            markers[ip].setLatLng(coords);
            try { markers[ip].setIcon(icon); } catch(e) {}
        } else {
            const m = L.marker(coords, { icon }).addTo(map);
            markers[ip] = m;
            const tip = `${ip}<br>${item.sys_org||''}<br>ASN: ${item.asn||''}<br>${item.network||''}`;
            m.bindTooltip(tip, { permanent:false, direction:'top', offset:[0,-10], className:'ip-tooltip' });
            m.on('click', () => openCctvModal(ip, item));
        }
    }
    document.getElementById('camCount').textContent = Object.keys(markers).length;
}

// ========= Search =========
document.getElementById('searchInput').addEventListener('input', function() {
    const q = this.value.trim().toLowerCase();
    const div = document.getElementById('searchResults');
    div.innerHTML = '';
    if (!q) return;
    for (let ip in dataStore) {
        const item = dataStore[ip];
        const text = `${ip} ${item.asn||''} ${item.network||''} ${item.sys_org||''}`.toLowerCase();
        if (text.includes(q)) {
            const el = document.createElement('div');
            el.className = 'searchItem';
            el.textContent = ip + (item.sys_org ? ' \u2014 ' + item.sys_org : '');
            el.onclick = () => {
                const p = (''+item.lalo).split(',').map(x => parseFloat(x));
                if (p.length >= 2) map.setView([p[0], p[1]], 10);
                if (markers[ip]) openCctvModal(ip, item);
                div.innerHTML = '';
                document.getElementById('searchInput').value = '';
            };
            div.appendChild(el);
        }
    }
});

// ========= Data =========
function loadData() {
    fetch('/api/data').then(r=>r.json()).then(data => {
        updateMarkers(data);
    }).catch(() => {});
}

loadData();
setInterval(loadData, 60000);

// ========= Hack The Camera =========
(function() {
    const hackBtn     = document.getElementById('hackBtn');
    const hackInput   = document.getElementById('hackIpInput');
    const hackLog     = document.getElementById('hackLog');
    const hackDot     = document.getElementById('hackStatusDot');
    const hackTxt     = document.getElementById('hackStatusTxt');
    let   activeEs    = null;

    function setStatus(state, msg) {
        hackTxt.textContent = msg;
        if (state === 'idle')    { hackDot.style.background = '#444'; }
        if (state === 'running') { hackDot.style.background = '#fa0'; hackDot.style.animation = 'blink 1s infinite'; }
        if (state === 'ok')      { hackDot.style.background = '#0f0'; hackDot.style.animation = ''; }
        if (state === 'err')     { hackDot.style.background = '#f44'; hackDot.style.animation = ''; }
    }

    function appendLog(text, cls) {
        hackLog.style.display = 'block';
        const line = document.createElement('div');
        if (cls) line.className = cls;
        line.textContent = text;
        hackLog.appendChild(line);
        hackLog.scrollTop = hackLog.scrollHeight;
    }

    function colorLine(raw) {
        const l = raw.toLowerCase();
        if (l.includes('success') || l.includes('found') || l.includes('[+]')) return 'hlog-ok';
        if (l.includes('error') || l.includes('fail') || l.includes('[-]')) return 'hlog-err';
        if (l.includes('[*]') || l.includes('trying') || l.includes('connecting')) return 'hlog-inf';
        return '';
    }

    function stopHack() {
        if (activeEs) { activeEs.close(); activeEs = null; }
        hackBtn.disabled = false;
        hackBtn.textContent = 'Hack';
    }

    hackBtn.addEventListener('click', function() {
        const target = hackInput.value.trim();
        if (!target) { hackInput.focus(); return; }
        if (!/^[\d\.]+:\d+$/.test(target)) {
            setStatus('err', 'Invalid format. Use ip:port');
            return;
        }
        if (activeEs) stopHack();

        hackLog.innerHTML = '';
        hackLog.style.display = 'block';
        hackBtn.disabled = true;
        hackBtn.textContent = 'Running...';
        setStatus('running', 'Hacking ' + target + '...');

        const es = new EventSource('/api/hack?target=' + encodeURIComponent(target));
        activeEs = es;

        es.addEventListener('log', (e) => {
            const txt = e.data;
            appendLog(txt, colorLine(txt));
        });

        es.addEventListener('done', (e) => {
            const code = parseInt(e.data, 10);
            stopHack();
            if (code === 0) {
                setStatus('ok', 'Completed');
                appendLog('[done] Exit 0', 'hlog-ok');
            } else {
                setStatus('err', 'Finished (exit ' + code + ')');
                appendLog('[done] Exit ' + code, 'hlog-err');
            }
        });

        es.onerror = () => {
            stopHack();
            setStatus('err', 'Connection lost');
            appendLog('[error] Stream disconnected', 'hlog-err');
        };
    });

    hackInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') hackBtn.click();
    });
})();
</script>
</body>
</html>
'''


@app.route('/')
def index():
    return HTML


@app.route('/api/data')
def api_data():
    reload_data()
    with _data_lock:
        return jsonify(_markers_data)


@app.route('/api/config', methods=['GET'])
def api_config_get():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            arr = json.load(f)
            if not isinstance(arr, list):
                arr = []
    except Exception:
        arr = []
    return jsonify(arr)


@app.route('/api/config', methods=['POST'])
def api_config_add():
    body = request.get_json(force=True, silent=True) or {}
    url = (body.get('url') or '').strip()
    if not url:
        return jsonify({"ok": False, "msg": "empty url"})
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            arr = json.load(f)
            if not isinstance(arr, list):
                arr = []
    except Exception:
        arr = []
    if url in arr:
        return jsonify({"ok": False, "msg": "url already exists"})
    arr.append(url)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True, "msg": ""})


@app.route('/api/config', methods=['DELETE'])
def api_config_remove():
    body = request.get_json(force=True, silent=True) or {}
    url = (body.get('url') or '').strip()
    if not url:
        return jsonify({"ok": False, "msg": "empty url"})
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            arr = json.load(f)
            if not isinstance(arr, list):
                arr = []
    except Exception:
        arr = []
    if url not in arr:
        return jsonify({"ok": False, "msg": "not found"})
    arr = [x for x in arr if x != url]
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True, "msg": ""})


# ---- MJPEG live stream ----

def generate_mjpeg(rtsp_url):
    cap = None
    try:
        os.environ.setdefault('OPENCV_FFMPEG_CAPTURE_OPTIONS', 'rtsp_transport;tcp')
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 8000)

        if not cap.isOpened():
            return

        consecutive_fail = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                consecutive_fail += 1
                if consecutive_fail > 10:
                    break
                time.sleep(0.1)
                continue
            consecutive_fail = 0

            ret2, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if not ret2:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                buf.tobytes() +
                b'\r\n'
            )
    except GeneratorExit:
        pass
    except Exception as e:
        log.error(f"[STREAM ERROR] {e}")
    finally:
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass


@app.route('/api/stream')
def api_stream():
    encoded = request.args.get('rtsp', '')
    if not encoded:
        return Response("Missing rtsp param", status=400)
    try:
        rtsp_url = base64.b64decode(encoded).decode('utf-8')
    except Exception:
        return Response("Invalid encoding", status=400)

    if not rtsp_url.startswith('rtsp://'):
        return Response("Invalid URL", status=400)

    return Response(
        generate_mjpeg(rtsp_url),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# ---- HTTP snapshot ----

SNAPSHOT_PATHS = [
    "/ISAPI/Streaming/channels/101/picture",
    "/onvif/snapshot/1",
    "/snapshot.cgi",
    "/cgi-bin/snapshot.cgi",
    "/image/jpeg.cgi",
    "/cgi-bin/viewer/video.jpg",
    "/axis-cgi/jpg/image.cgi",
    "/jpg/image.jpg",
    "/video.cgi?sessionid=0",
    "/snap.jpg",
    "/snapshot",
    "/shot.jpg",
]


@app.route('/api/snapshot/<ip>')
def api_snapshot(ip):
    if not re.match(r'^[\d\.]+$', ip):
        return Response("Invalid IP", status=400)

    hdrs = {"User-Agent": "Mozilla/5.0", "Accept": "image/jpeg,image/*,*/*"}
    for port in [80, 8080, 8000, 443]:
        for path in SNAPSHOT_PATHS:
            scheme = "https" if port == 443 else "http"
            url = f"{scheme}://{ip}:{port}{path}"
            try:
                resp = requests.get(url, timeout=3, verify=False, headers=hdrs, stream=True)
                ct = resp.headers.get("Content-Type", "")
                if resp.status_code == 200 and ("image" in ct or "jpeg" in ct):
                    data = resp.content
                    if len(data) > 500:
                        return Response(data, content_type=ct or "image/jpeg")
            except Exception:
                pass

    return Response("No snapshot available", status=404)


# ---- Hack stream (SSE) ----

def _sse(event, data):
    return f"event: {event}\ndata: {data}\n\n"


_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[mGKHFABCDJsr]')

def _strip_ansi(text):
    return _ANSI_RE.sub('', text)


@app.route('/api/hack')
def api_hack():
    target = request.args.get('target', '').strip()
    if not re.match(r'^[\d\.]+:\d+$', target):
        def bad():
            yield _sse('done', '1')
        return Response(bad(), mimetype='text/event-stream')

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bloodcat.py')
    env = {**os.environ, 'PYTHONUNBUFFERED': '1'}

    def generate():
        try:
            proc = subprocess.Popen(
                [sys.executable, '-u', script, '--ip', target],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=env
            )
            header_passed = False
            buf = b''
            while True:
                chunk = proc.stdout.read(1)
                if not chunk:
                    break
                buf += chunk
                if chunk == b'\n':
                    line = _strip_ansi(buf.decode('utf-8', errors='replace')).rstrip()
                    buf = b''
                    if not header_passed:
                        # Skip the ASCII art logo until we see the version/header banner
                        if 'Blood Cat' in line or 'Maptnh' in line:
                            header_passed = True
                        continue
                    if line:
                        yield _sse('log', line)
            if buf:
                line = _strip_ansi(buf.decode('utf-8', errors='replace')).rstrip()
                if header_passed and line:
                    yield _sse('log', line)
            proc.wait()
            yield _sse('done', str(proc.returncode))
        except Exception as e:
            yield _sse('log', f'[error] {e}')
            yield _sse('done', '1')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == "__main__":
    print(LOGO)
    threading.Thread(target=start_bc_server, daemon=True).start()
    log.info(f"BlackEYE web server starting on http://0.0.0.0:{WEB_PORT}")
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False, threaded=True)
