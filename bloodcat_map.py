#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import os
import sys
import json
import re
import subprocess
from lib.camlib import *
from lib.log_cat import *
 
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import (
    Qt, QUrl, QTimer, QObject, pyqtSlot, QThread, pyqtSignal,
    QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from lib.version import VERSION
log = LogCat()
cam = CamLib()
 
CONFIG_PATH = os.path.join('.', 'data', 'bloodcatmap.conf')
SLOT_COUNT = 10  
API_SER = 34713
CHAT_SER = 34413 

os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)


HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>BloodCat Map @ S-H4CK13</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html, body, #map { height: 100%; margin:0; padding:0; background-color:#000; }

.cursor-map { cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="24"><text x="0" y="18" font-size="18" fill="lime" font-weight="bold">[ ]</text></svg>') 12 12, auto !important; }
.cursor-marker, .cursor-marker:hover { cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><text x="0" y="18" font-size="18" fill="lime" font-weight="bold">[+]</text></svg>') 12 12, pointer !important; }

.ip-tooltip{ background: rgba(0,0,0,0.78); color:#fff; font-size:12px; padding:6px 10px; border-radius:6px; pointer-events: none; }
.leaflet-marker-icon {
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><text x="0" y="18" font-size="18" fill="lime" font-weight="bold">[+]</text></svg>') 12 12, pointer !important;
}

#searchBox { position:absolute; top:10px; right:10px; z-index:9999; background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:220px; font-family:"Segoe UI", Arial, sans-serif; }

#searchInput { width:100%; padding:4px 6px; border-radius:4px; border:none; outline:none; background:#222; color:#0f0;}
#searchResults { max-height:150px; overflow-y:auto; margin-top:4px; font-size:12px;}
.searchItem { padding:4px; cursor:pointer;}
.searchItem:hover { background: rgba(0,255,0,0.2); }


#statusBox { position:absolute; left:10px; bottom:10px; z-index:9999; background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:320px; font-family:"Segoe UI", Arial, sans-serif; box-sizing:border-box; display:flex; flex-direction:column; }
#statusHeader { display:flex; align-items:center; gap:8px; font-size:13px; margin-bottom:6px; }
.statusDot { width:10px; height:10px; border-radius:50%; display:inline-block; background:#888; box-shadow:0 0 6px rgba(0,0,0,0.6); }


#urlRow { display:flex; gap:6px; margin-bottom:6px; }
#urlInput { flex:1; padding:6px; border-radius:4px; border:none; outline:none; background:#222; color:#0f0; font-size:12px; }
#urlBtn { padding:6px 8px; border-radius:4px; border:none; background:#0a0; color:#000; cursor:pointer; font-weight:bold; }


#statusList { max-height:160px; overflow-y:auto; font-size:12px; padding-top:4px; }
#statusList::-webkit-scrollbar { width:6px; }
#statusList::-webkit-scrollbar-track { background:rgba(0,0,0,0.3); border-radius:3px; }
#statusList::-webkit-scrollbar-thumb { background:rgba(0,255,0,0.5); border-radius:3px; }

.statusItem { display:flex; align-items:center; gap:8px; padding:6px; cursor:pointer; border-radius:4px; background: rgba(255,255,255,0.01); }
.statusItem:hover { background: rgba(0,255,0,0.04); }
.statusThumb { width:36px; height:22px; object-fit:cover; border-radius:3px; border:1px solid rgba(255,255,255,0.06); background:#111; }
.statusText { color:#0f0; font-size:12px; margin-left:6px; }
.statusSub { color:#ccc; font-size:11px; margin-left:auto; margin-right:8px; }
.delBtn { background:transparent; border:1px solid rgba(255,255,255,0.06); color:#f77; padding:2px 6px; border-radius:3px; cursor:pointer; font-weight:bold; }
#chatBox {
    margin-top: 6px;
    background: rgba(0,0,0,0.7);
    border-radius: 6px;
    padding: 6px;
    font-family: "Segoe UI", Arial, sans-serif;

    height: 200px;
    max-height: 200px;
    box-sizing: border-box;

    display: flex;
    flex-direction: column;
}
#chatLog {
    flex: 1;
    overflow-y: auto;
    font-size: 12px;
    color: #0f0;
    word-break: break-all;
}
#chatInputRow {
    flex-shrink: 0;
    display: flex;
    gap: 6px;
    margin-top: 6px;
}
#chatInput {
    flex:1;
    padding:4px 6px;
    border-radius:4px;
    border:none;
    outline:none;
    background:#222;
    color:#0f0;
}
#chatSend {
    padding:4px 8px;
    border-radius:4px;
    border:none;
    background:#0a0;
    color:#000;
    font-weight:bold;
    cursor:pointer;
}
.chatLine {
    margin-bottom:4px;
}
 
@media (max-width:480px){ #statusBox { width:260px; } #searchBox { width:180px; } }

</style>
</head>
<body>

<div id="map" class="cursor-map"></div>

<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / ASN / Network"/>
    <div id="searchResults"></div>
    <div id="chatBox">
    <div id="chatLog"></div>
    <div id="chatInputRow">
        <input id="chatInput" placeholder="Send message..." />
        <button id="chatSend">Send</button>
    </div>
</div>
</div>

<div id="statusBox" aria-live="polite">
    <div id="statusHeader">
        <span class="statusDot" id="dbDot" title="DB status"></span>
        <strong>Remote Databases</strong>
    </div>
    <div id="urlRow">
        <input id="urlInput" placeholder="Enter remote DB URL (http://...)"/>
        <button id="urlBtn">Get</button>
    </div>
    <div id="statusList"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
let map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; <a href="https://www.openstreetmap.org/">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains:'abcd', maxZoom:19
}).addTo(map);

 

let markers = {}, rtspMap = {}, dataStore = {};
const iconCache = {};
function getIconForPath(path){ if(!path) return icon_main; if(iconCache[path]) return iconCache[path]; try{ const ic=L.icon({iconUrl:path,iconSize:[32,32],iconAnchor:[16,32]}); iconCache[path]=ic; return ic;}catch(e){return icon_main;} }

let bridge=null;
new QWebChannel(qt.webChannelTransport,function(channel){
    bridge=channel.objects.bridge;
    console.log('WebChannel initialized, bridge=',bridge);
    window.renderStatusList(); 
});

 
function getRemoteUrlsAsync(cb){
    try{
        const maybe = bridge && bridge.getRemoteUrls && bridge.getRemoteUrls();
        if(typeof maybe==='string'){ setTimeout(()=>{try{cb(JSON.parse(maybe||'[]'))}catch(e){cb([])}},0); return;}
    }catch(e){}
    try{
        bridge.getRemoteUrls(function(s){ setTimeout(()=>{try{cb(JSON.parse(s||'[]'))}catch(e){cb([])}},0); });
    }catch(e){ setTimeout(()=>cb([]),0);} 
}

let renderPending=null, renderInProgress=false;
function scheduleRenderStatusList(delay=100){ if(renderPending) clearTimeout(renderPending); renderPending=setTimeout(()=>{ renderPending=null; if(renderInProgress){ scheduleRenderStatusList(120); return;} doRenderStatusList(); }, delay); }
document.getElementById('searchInput').addEventListener('input', function() {
    const q = this.value.trim().toLowerCase();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    if (!q) return;

    for (let ip in dataStore) {
        const item = dataStore[ip];
        const text = `${ip} ${item.asn||''} ${item.network||''} ${item.sys_org||''}`.toLowerCase();
        if (text.includes(q)) {
            const div = document.createElement('div');
            div.className = 'searchItem';
            div.textContent = ip + (item.sys_org ? ' - ' + item.sys_org : '');
            div.onclick = () => {
                
                const coords = (''+item.lalo).split(',').map(x=>parseFloat(x));
                if (coords.length>=2) map.setView([coords[0], coords[1]],10);
                if (markers[ip]) markers[ip].openPopup();
            };
            resultsDiv.appendChild(div);
        }
    }
});
function doRenderStatusList(){
    renderInProgress=true;
    const statusListDiv=document.getElementById('statusList'); statusListDiv.innerHTML='';
    const slotCount=10;
    getRemoteUrlsAsync(function(remoteUrls){
        try{
            remoteUrls = remoteUrls||[];
            const clean=[]; const seen=new Set();
            for(let u of remoteUrls){ if(!u) continue; u=String(u).trim(); if(!u) continue; if(seen.has(u)) continue; seen.add(u); clean.push(u); if(clean.length>=slotCount) break;}
            for(let i=0;i<slotCount;i++){
                const slotIdx=i+1;
                const img=`./color_${slotIdx}.png`;
                const url=clean[i]||null;
                const displayText=url?(url.length>32?url.slice(0,30)+'..':url):'Empty';
                const div=document.createElement('div'); div.className='statusItem';
                div.className = 'statusItem cursor-marker';
                div.innerHTML=`
                    <img src="${img}" class="statusThumb" alt="thumb"/>
                    <div class="statusText" title="${url||''}">${displayText}</div>
                    <div class="statusSub">[x_x]</div>
                    <button class="delBtn" data-slot="${i}" title="Remove">x</button>`;
                div.onclick=(ev)=>{ if(ev.target&&ev.target.classList&&ev.target.classList.contains('delBtn')) return; if(!url) return;
                    let ipFound=null; for(let ip in dataStore){ try{ if(dataStore[ip]&&dataStore[ip].source_url===url){ipFound=ip; break;} }catch(e){} }
                    if(ipFound && dataStore[ipFound] && dataStore[ipFound].lalo){ const parts=(''+dataStore[ipFound].lalo).split(',').map(x=>parseFloat(x)); if(parts.length>=2) map.setView([parts[0],parts[1]],10); if(markers[ipFound]) markers[ipFound].openPopup(); }
                    else setIpSubStatus('', 'No host mapped');
                };
                const delBtn=div.querySelector('.delBtn'); 
                delBtn.onclick=(ev)=>{ ev.stopPropagation(); const slot=parseInt(ev.target.getAttribute('data-slot')); if(!clean[slot]){ setIpSubStatus(displayText,'Nothing'); return;}
                    const targetUrl=clean[slot]; try{ if(bridge&&bridge.removeRemoteUrl){ const res=bridge.removeRemoteUrl(targetUrl); setTimeout(()=>{ try{ const obj=JSON.parse(res); if(obj.ok){ setIpSubStatus(displayText,'Removed'); scheduleRenderStatusList(120); } else { setIpSubStatus(displayText,'Remove failed'); } }catch(e){ setIpSubStatus(displayText,'Removed'); scheduleRenderStatusList(120); } },0);} else { setIpSubStatus(displayText,'No bridge');} }catch(e){console.warn(e); setIpSubStatus(displayText,'Error');}
                };
                statusListDiv.appendChild(div);
            }
            console.log('[doRenderStatusList] sanitized:', clean);
        }finally{ setTimeout(()=>{ renderInProgress=false; },60);} 
    });
}
window.renderStatusList=function(){ scheduleRenderStatusList(0); };

function updateMarkers(data_obj){
    dataStore=data_obj||{};
    for(let ip in markers){ if(!(ip in dataStore)){ map.removeLayer(markers[ip]); delete markers[ip]; delete rtspMap[ip];} }
    for(let ip in dataStore){
        const item=dataStore[ip]; const parts=(''+item.lalo).split(',').map(x=>parseFloat(x)); if(parts.length<2||isNaN(parts[0])||isNaN(parts[1])) continue;
        const coords=[parts[0],parts[1]]; rtspMap[ip]=item.rtsp;
        let chosenIcon=getIconForPath(item.icon);
        if(markers[ip]){ markers[ip].setLatLng(coords); try{ markers[ip].setIcon(chosenIcon);}catch(e){} } 
        else{
            const m=L.marker(coords,{icon:chosenIcon}).addTo(map); markers[ip]=m;
            const infoHtml=`${ip}<br>${item.sys_org||''}<br>ASN: ${item.asn||''}<br>${item.network||''}`;
            m.bindTooltip(infoHtml,{permanent:false,direction:'top',offset:[0,-35],className:'ip-tooltip'});
            m.bindPopup(infoHtml);
            m.on('click',()=>{ if(bridge && bridge.playRTSP) { try{ bridge.playRTSP(item.rtsp); }catch(e){console.error('bridge.playRTSP error',e);} } });
        }
    }
    window.renderStatusList();
}

function setDbStatus(status){ const dbDot=document.getElementById('dbDot'); let color='#888'; const s=(status||'').toLowerCase(); if(s==='connected'||s==='ok'||s==='online') color='#0f0'; else if(s==='degraded'||s==='partial') color='#ffa500'; else if(s==='disconnected'||s==='down'||s==='offline') color='#f00'; dbDot.style.background=color; }
function setIpSubStatus(ip,text){ const subElems=document.querySelectorAll('.statusItem .statusText'); for(const el of subElems){ if(el.textContent===ip){ const sub=el.parentNode.querySelector('.statusSub'); if(sub) sub.textContent=text; break;}} window.renderStatusList(); }

document.addEventListener('DOMContentLoaded',function(){
    const urlBtn=document.getElementById('urlBtn'); const urlInput=document.getElementById('urlInput');
    urlBtn.addEventListener('click',()=>{ const url=(urlInput.value||'').trim(); if(!url) return; if(!bridge||!bridge.addRemoteUrl){ alert('Bridge not ready'); return;}
        try{ const res=bridge.addRemoteUrl(url); try{ const obj=JSON.parse(res); if(obj.ok){ urlInput.value=''; window.renderStatusList(); setIpSubStatus('','Added');} else{ alert('Add failed: '+(obj.msg||''));} }catch(e){ window.renderStatusList(); } }catch(e){ console.warn(e);} });
});
const snapRadius = 20;

map.on('mousemove', function(e){
    const mousePoint = map.latLngToContainerPoint(e.latlng);
    for(let ip in markers){
        const marker = markers[ip];
        if(!marker) continue;
        const icon = marker.options.icon.options;
        const iconSize = icon.iconSize || [32,32];
        const iconAnchor = icon.iconAnchor || [16,32];

        const markerPoint = map.latLngToContainerPoint(marker.getLatLng());
        const centerOffsetX = iconSize[0]/2 - iconAnchor[0];
        const centerOffsetY = iconSize[1]/2 - iconAnchor[1];
        const centerPoint = L.point(markerPoint.x + centerOffsetX, markerPoint.y + centerOffsetY);

        const dx = centerPoint.x - mousePoint.x;
        const dy = centerPoint.y - mousePoint.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if(dist <= snapRadius){
            if(bridge && bridge.snapMouse){
                bridge.snapMouse(centerPoint.x, centerPoint.y);
            }
            break;
        }
    }
});
function escapeHtml(str){
    return String(str)
        .replace(/&/g,"&amp;")
        .replace(/</g,"&lt;")
        .replace(/>/g,"&gt;")
        .replace(/"/g,"&quot;")
        .replace(/'/g,"&#39;");
}

function appendChatLine(text){
    const div = document.createElement("div");
    div.className = "chatLine";
    div.innerHTML = escapeHtml(text);
    const log = document.getElementById("chatLog");
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

document.getElementById("chatSend").onclick = sendChat;
document.getElementById("chatInput").addEventListener("keydown", e=>{
    if(e.key==="Enter") sendChat();
});

function sendChat(){
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if(!msg) return;
    input.value = "";
    if(bridge && bridge.sendChat){
        bridge.sendChat(msg);
    }
}
</script>
</body>
</html>

'''

LOGO = "\033[38;5;208m"+r'''
                                               .--.
                                               `.  \
                                                 \  \
                                                  .  \
                                                  :   .
                                                  |    .
                                                  |    :
                                                  |    |
  ..._  ___                                       |    |
 `."".`---'""--..___                              |    |
 ,-\  \             ""-...__         _____________/    |
 / ` " '                    `"""""""""                  .
 \                                                      L
 (>                                                      \
/                                                         \
\_    ___..---.                                            L
  `--'         '.                                           \
                 .                                           \_
                _/`.                                           `.._
             .'     -.                                             `.
            /     __.-Y     /''''''-...___,...--------.._            |
           /   _."    |    /                ' .      \   '---..._    |
          /   /      /    /                _,. '    ,/           |   |
          \_,'     _.'   /              /''     _,-'            _|   |
                  '     /               `-----''               /     |
                  `...-'                                       `...
[Maptnh@S-H4CK13]      [Blood Cat Map '''+VERSION+r''']    [https://github.com/MartinxMax]'''+"\033[0m"


class GlobalBCHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join('.', 'data'), **kwargs)

    def do_GET(self):
        if self.path.strip("/") != "global.bc":
            self.send_error(403, "Forbidden")
            return
        return super().do_GET()

def start_udp_listener(win):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", CHAT_SER))
    log.info(f"BloodCat-Map chat service started...")
    while True:
        try:
            data, addr = s.recvfrom(4096)
            res = cam.aes_decrypt(data)
            txt = json.loads(res)["msg"]
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            line = f"({ts}){addr[0]}: {txt}"
            msg = json.dumps(line, ensure_ascii=False)
            js = f'appendChatLine({msg});'
            win.view.page().runJavaScript(js)
        except Exception as e:
            log.error(f"[CHAT RECV ERROR] {e}")
        


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
    server_address = ("0.0.0.0", API_SER)
    httpd = HTTPServer(server_address, GlobalBCHandler)
    local_ip = get_local_ip() 
    log.info(f"BloodCat-Map API local data download link: http://{local_ip}:{API_SER}/global.bc")
    httpd.serve_forever()

 

class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = None
    @pyqtSlot(int, int)
    def snapMouse(self, x, y):
        global_pos = self.parent_window.view.mapToGlobal(QPoint(x, y))
        QCursor.setPos(global_pos)
    @pyqtSlot(str)

    def sendChat(self, msg):
        try:
            msg = json.dumps({"msg": msg}, ensure_ascii=False)
            payload = cam.aes_encrypt(msg)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(payload, ("255.255.255.255", 34413))
            s.close()
        except Exception as e:
            log.error(f"[CHAT SEND ERROR] {e}")

    @pyqtSlot(str)
    def playRTSP(self, url):
        match = re.search(r'@([\d\.]+):', url)
        ip = match.group(1) if match else 'N/A'

        log.info(f"Now playing... [{ip}]")

        subprocess.Popen([
            "python3.14", 
            "./lib/play.py",
            url,
            ip,
            'origin'
        ])

    @pyqtSlot(str, result=str)
    def addRemoteUrl(self, url):
        try:
            url = url.strip()
            if not url:
                return json.dumps({"ok": False, "msg": "empty url"})
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    arr = json.load(f)
                    if not isinstance(arr, list): arr = []
            except Exception:
                arr = []
            if url in arr:
                return json.dumps({"ok": False, "msg": "url exists"})
            arr.append(url)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(arr, f, ensure_ascii=False, indent=2)
            if hasattr(self, 'parent_window') and self.parent_window:
                try:
                    self.parent_window.start_data_loader()
                except Exception as e:
                    print("start_data_loader failed:", e)
            return json.dumps({"ok": True, "msg": ""})
        except Exception as e:
            return json.dumps({"ok": False, "msg": str(e)})

    @pyqtSlot(str, result=str)
    def removeRemoteUrl(self, url):
        try:
            url = url.strip()
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    arr = json.load(f)
                    if not isinstance(arr, list): arr = []
            except Exception:
                arr = []
            if url not in arr:
                return json.dumps({"ok": False, "msg": "not found"})
            arr = [x for x in arr if x != url]
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(arr, f, ensure_ascii=False, indent=2)
            if hasattr(self, 'parent_window') and self.parent_window:
                try:
                    self.parent_window.start_data_loader()
                except Exception as e:
                    print("start_data_loader failed:", e)
            return json.dumps({"ok": True, "msg": ""})
        except Exception as e:
            return json.dumps({"ok": False, "msg": str(e)})

    @pyqtSlot(result=str)
    def getRemoteUrls(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                arr = json.load(f)
                if not isinstance(arr, list):
                    arr = []
        except Exception:
            arr = []
        return json.dumps(arr)

    @pyqtSlot(result=str)
    def getDbStatus(self):
        return "N/A"


class DataLoader(QThread):
    remoteLoaded = pyqtSignal(dict)
    localLoaded = pyqtSignal(dict)

    def __init__(self, remote_urls=None, parent=None):
        super().__init__(parent)
        self.remote_urls = remote_urls or []

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
                    "icon": icon_path or "./color_1.png",
                    "source_url": source_url or ""
                }

        if isinstance(raw, str):
            for line in raw.splitlines():
                line = line.strip()
                if not line: continue
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
            else:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        process_obj(parsed)
                except Exception:
                    pass

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
                    try:
                        remote_raw = cam.get_DB_data(url)
                    except Exception as e:
                        print("cam.get_DB_data(url) error:", e)
                    if not remote_raw:
                        continue
                    slot_index = (idx % SLOT_COUNT) + 1
                    icon_path = f"./color_{slot_index}.png"
                    parsed = self.parse_raw_to_dict(remote_raw, 'remote', source_url=url, icon_path=icon_path)
                    for k,v in parsed.items():
                        remote_merged[k] = v
                except Exception as e:
                    print("Error processing remote url", url, e)
                    continue
        except Exception as e:
            print("DataLoader remote part error:", e)

        self.remoteLoaded.emit(remote_merged)
        return


class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BloodCat Map @ S-H4CK13    [https://github.com/MartinxMax]")
        self.resize(1280, 800)

        icon_path = os.path.join(os.path.dirname(__file__), "ico.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.view = QWebEngineView()
        self.layout.addWidget(self.view)

        self.wait_label = QLabel(self)
        self.wait_label.setAlignment(Qt.AlignCenter)
        self.wait_label.setStyleSheet("background-color: rgba(0,0,0,1);")
        self.wait_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.wait_label.setAttribute(Qt.WA_NoSystemBackground)
        self.wait_label.setCursor(Qt.BlankCursor)
        wait_path = os.path.join(os.path.dirname(__file__),"location", "wait.jpg")
        self.wait_pixmap = None
        if os.path.exists(wait_path):
            self.wait_pixmap = QPixmap(wait_path)
            self._update_wait_pixmap()
        else:
            print(f"\033[31m[!] No found background: {wait_path}\033[0m")

        self.wait_label.raise_()
        self.wait_label.show()
        self.html_path = os.path.join(os.path.dirname(__file__),"location","map_temp.html")
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(HTML)
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.bridge.parent_window = self
        self.channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.channel)

        self.last_data = {}
        self.remote_data = {}
        self.local_data = {}
        self.merged_data = {}

        self.view.loadFinished.connect(self.on_load_finished)
        self.view.load(QUrl.fromLocalFile(os.path.abspath(self.html_path)))

    def _update_wait_pixmap(self):
        if not self.wait_pixmap:
            self.wait_label.setFixedSize(self.size())
            return
        scaled = self.wait_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.wait_label.setPixmap(scaled)
        self.wait_label.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_wait_pixmap()

    def _stop_current_animation(self):
        try:
            if hasattr(self, 'anim_group') and self.anim_group:
                self.anim_group.stop()
        except Exception:
            pass

    def _setup_wait_animation(self, loop=True, loop_count=-1):
        self._stop_current_animation()

        self._opacity_effect = QGraphicsOpacityEffect(self.wait_label)
        self.wait_label.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        anim1 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim1.setDuration(1500)
        anim1.setStartValue(1.0)
        anim1.setEndValue(0.2)
        anim1.setEasingCurve(QEasingCurve.InOutSine)

        anim2 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim2.setDuration(1500)
        anim2.setStartValue(0.2)
        anim2.setEndValue(1.0)
        anim2.setEasingCurve(QEasingCurve.InOutSine)

        anim3 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim3.setDuration(1000)
        anim3.setStartValue(1.0)
        anim3.setEndValue(0.0)
        anim3.setEasingCurve(QEasingCurve.InOutQuad)
        anim3.finished.connect(lambda: [
            self.wait_label.hide(),
            self.view.raise_()
        ])

        if not self.wait_label.isVisible():
            self.wait_label.show()

        if loop:
            loop_group = QSequentialAnimationGroup()
            loop_group.addAnimation(anim1)
            loop_group.addAnimation(anim2)
            loop_group.setLoopCount(loop_count)
            loop_group.finished.connect(lambda: anim3.start())
            loop_group.start()
            self.anim_group = loop_group
        else:
            seq = QSequentialAnimationGroup()
            seq.addAnimation(anim1)
            seq.addAnimation(anim2)
            seq.addAnimation(anim3)
            seq.start()
            self.anim_group = seq

    def on_load_finished(self, ok):
        if not ok:
            print("\033[31m[!] BloodCat config file load failed... please check your network...\033[0m")
            return
        self.start_data_loader()

    def start_data_loader(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                remote_urls = json.load(f)
                if not isinstance(remote_urls, list):
                    remote_urls = []
        except Exception:
            remote_urls = []
        self.loader = DataLoader(remote_urls=remote_urls)
        self.loader.remoteLoaded.connect(self._handle_remote_loaded)
        self.loader.localLoaded.connect(self._handle_local_loaded)
        self.loader.start()

    def _run_update_js(self, data_dict):
        try:
            js = "updateMarkers(%s);" % json.dumps(data_dict, ensure_ascii=False)
            self.view.page().runJavaScript(js)
        except Exception as e:
            print("\033[31m[!] runJavaScript failed:", e, "\033[0m")

    def _handle_remote_loaded(self, remote_dict):
        log.info("Remote loaded: %d items" % len(remote_dict))
        self.remote_data = remote_dict or {}
        self.merged_data = dict(self.remote_data)
        self._run_update_js(self.merged_data)
        self._setup_wait_animation(loop=True, loop_count=1)

    def _handle_local_loaded(self, local_dict):
        log.info("Local loaded: %d items" % len(local_dict))
        self.local_data = local_dict or {}
        merged = dict(self.remote_data)
        for ip, local_item in (self.local_data.items() if self.local_data else {}):
            if ip in merged:
                remote_item = merged[ip]
                lalo_to_use = remote_item.get("lalo", "")
 
                icon_to_use = remote_item.get("icon", "./color_1.png")
                merged[ip] = {
                    "rtsp": local_item.get("rtsp", remote_item.get("rtsp", "")),
                    "lalo": lalo_to_use,
                    "sys_org": local_item.get("sys_org", remote_item.get("sys_org", "")),
                    "asn": local_item.get("asn", remote_item.get("asn", "")),
                    "network": local_item.get("network", remote_item.get("network", "")),
                    "source": "local",
                    "icon": icon_to_use,
                    "source_url": remote_item.get("source_url", "")
                }
            else:
                merged[ip] = local_item
        self.merged_data = merged
        self._run_update_js(self.merged_data)
    
if __name__ == "__main__":
    print(LOGO)
    threading.Thread(target=start_http_server, daemon=True).start()
    app = QApplication(sys.argv)
    win = MapWindow()
    threading.Thread(
    target=start_udp_listener,
    args=(win,),
    daemon=True
        ).start()

    win.showMaximized()
    sys.exit(app.exec_())
