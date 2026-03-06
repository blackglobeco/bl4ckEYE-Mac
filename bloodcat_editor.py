#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import sys
import re
import json
import csv
import os
import ipaddress
from lib.version import VERSION
from collections import OrderedDict
from typing import List, Dict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QFileDialog,
    QLabel, QMessageBox, QGroupBox, QDialog,
    QFormLayout, QDialogButtonBox, QFrame, QStatusBar
)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
from lib.location import Location
from lib.camlib import CamLib
from lib.version import VERSION

LOGO = r'''
             *     ,MMM8&amp;&amp;&amp;.            *
                  MMMM88&amp;&amp;&amp;&amp;&amp;    .
                 MMMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;
     *           MMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;&amp;
                 MMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;&amp;
                 'MMM88&amp;&amp;&amp;&amp;&amp;&amp;'
                   'MMM8&amp;&amp;&amp;'      *    _
          |\___/|                      \\
          )     (    |\_/|              ||    '
         =\     /=   )a a '._.-""""-.  //
           )===(    =\T_= /    ~  ~  \//
          /     \     `"`\   ~   / ~  /
          |     |         |~   \ |  ~/
         /       \         \  ~/- \ ~\
         \       /         || |  // /`
  aac_/\_/\_   _/_/\_/\_/\_((_|\((_//\_/\_/\_
  |  |  |  |( (  |  |  |  |  |  |  |  |  |  |
  |  |  |  | ) ) |  |  |  |  |  |  |  |  |  |
  |  |  |  |(_(  |  |  |  |  |  |  |  |  |  |      
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
Maptnh@S-H4CK13   Bloodcat '''+VERSION+r''' Hikvision bc & csv Editor  https://github.com/MartinxMax'''

HTML_MAP = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Geographic Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html, body, #map { height: 100%; margin:0; padding:0; background-color:#000; }
.cursor-map { cursor: auto !important; }
.ip-tooltip{ background: rgba(0,0,0,0.78); color:#fff; font-size:12px; padding:6px 10px; border-radius:6px; pointer-events: none; }
#searchBox { position:absolute; top:10px; right:10px; z-index:9999; background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:260px; font-family:"Segoe UI", Arial, sans-serif; }
#searchInput { width:100%; padding:6px; border-radius:4px; border:none; outline:none; background:#222; color:#0f0;}
#searchResults { max-height:200px; overflow-y:auto; margin-top:6px; font-size:12px;}
.searchItem { padding:6px; cursor:pointer; color:#0f0; border-radius:4px; }
.searchItem:hover { background: rgba(0,255,0,0.08); }
</style>
</head>
<body>
<div id="map" class="cursor-map"></div>
<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / ASN / Network / Org" />
    <div id="searchResults"></div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM & CARTO',
    subdomains:'abcd', maxZoom:19
}).addTo(map);
let markers = {}, dataStore = {};
const iconCache = {};
function getIconForPath(path){
    if(!path) return null;
    if(iconCache[path]) return iconCache[path];
    try{
        const ic = L.icon({
            iconUrl: path,
            iconSize: [28,28],
            iconAnchor: [14,28],
            popupAnchor: [0,-26]
        });
        iconCache[path] = ic;
        return ic;
    } catch(e){
        console.warn('getIconForPath failed', path, e);
        return null;
    }
}
function updateMarkers(data_obj){
    dataStore = data_obj || {};
    for(let ip in markers){
        if(!(ip in dataStore)){
            try { map.removeLayer(markers[ip]); } catch(e){}
            delete markers[ip];
        }
    }
    for(let ip in dataStore){
        const item = dataStore[ip];
        const parts = (''+item.lalo).split(',').map(x=>parseFloat(x));
        if(parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) continue;
        const coords = [parts[0], parts[1]];
        let chosenIcon = null;
        if(item.icon){
            chosenIcon = getIconForPath(item.icon);
        }
        const markerOptions = {};
        if(chosenIcon) markerOptions.icon = chosenIcon;
        if(markers[ip]){
            markers[ip].setLatLng(coords);
            try { if(chosenIcon) markers[ip].setIcon(chosenIcon); } catch(e){}
        } else {
            const m = L.marker(coords, markerOptions).addTo(map);
            markers[ip] = m;
            const infoHtml = `${ip}<br>${item.sys_org||''}<br>ASN: ${item.asn||''}<br>${item.network||''}`;
            m.bindTooltip(infoHtml, {permanent:false, direction:'top', offset:[0,-35], className:'ip-tooltip'});
            m.bindPopup(infoHtml);
        }
    }
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    if(q) renderSearchResults(q);
}
function renderSearchResults(q){
    q = (q||'').toLowerCase();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    if(!q) return;
    for(let ip in dataStore){
        try{
            const it = dataStore[ip];
            const text = `${ip} ${it.asn||''} ${it.network||''} ${it.sys_org||''}`.toLowerCase();
            if(text.includes(q)){
                const div = document.createElement('div');
                div.className = 'searchItem';
                div.textContent = ip + (it.sys_org ? ' - ' + it.sys_org : '');
                div.onclick = (ev) => {
                    if(markers[ip]){
                        const latlng = markers[ip].getLatLng();
                        map.setView(latlng, 9);
                        markers[ip].openPopup();
                    } else {
                        const parts = (''+it.lalo).split(',').map(x=>parseFloat(x));
                        if(parts.length>=2 && !isNaN(parts[0]) && !isNaN(parts[1])){
                            map.setView([parts[0], parts[1]], 9);
                        }
                    }
                };
                resultsDiv.appendChild(div);
            }
        }catch(e){}
    }
}
document.getElementById('searchInput').addEventListener('input', function(){
    const q = this.value.trim().toLowerCase();
    renderSearchResults(q);
});
</script>
</body>
</html>
'''

class MapDialog(QDialog):
    def __init__(self, parent=None, markers_data=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setSizeGripEnabled(True)
        self.setWindowTitle("Geographic Location Map")
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        w = int(geo.width() * 0.7)
        h = int(geo.height() * 0.7)
        x = (geo.width() - w) // 2
        y = (geo.height() - h) // 2
        self.setGeometry(x, y, w, h)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if not WEB_ENGINE_AVAILABLE:
            label = QLabel("PyQtWebEngine is not installed; map cannot be displayed.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
            layout.addWidget(label)
            return
        self.view = QWebEngineView()
        layout.addWidget(self.view)
        base = QUrl.fromLocalFile(os.getcwd() + os.sep)
        self.view.setHtml(HTML_MAP, base)
        def on_load_finished(ok):
            if ok:
                data = markers_data or {}
                js_data = json.dumps(data, ensure_ascii=False)
                self.view.page().runJavaScript(f"updateMarkers({js_data});")
            else:
                QMessageBox.warning(self, "Error", "Map page failed to load")
        self.view.loadFinished.connect(on_load_finished)

class BCDataLoader:
    def __init__(self):
        self.cam = CamLib()  
        self.all_data: List[Dict] = []
        self.filtered_data: List[Dict] = []

    def import_bc_file(self, path_file: str) -> bool:
 
        try:
            bc_data = self.cam.get_LocalDB_data(path_file)
            if not isinstance(bc_data, list):
                raise ValueError("BC data must be a list of dicts")
            self.all_data.clear()
            for item in bc_data:
                if not isinstance(item, dict):
                    continue
                rtsp = item.get("rtsp", "")
                data = item.get("data", {}) or {}
                self.all_data.append({
                    "rtsp": rtsp,
                    "country": data.get("country", "unknown") or "unknown",
                    "city": data.get("city", "unknown") or "unknown",
                    "user": self.extract_user_pass(rtsp)[0],
                    "password": self.extract_user_pass(rtsp)[1],
                    "lalo": data.get("lalo", ""),
                    "asn": data.get("asn", ""),
                    "sys_org": data.get("sys_org", ""),
                    "network": data.get("network", ""),
                    "selected": False
                })
            self.filtered_data = self.all_data.copy()
            return True
        except Exception as e:
            QMessageBox.critical(None, "Import Error", f"Failed to import BC file: {str(e)}")
            return False

    @staticmethod
    def extract_user_pass(rtsp: str) -> tuple:
        match = re.match(r"rtsp://([^:]+):([^@]+)@.*", rtsp)
        return match.groups() if match else ("", "")

    def global_filter_data(self, keyword: str):
        kw = keyword.lower().strip()
        if not kw:
            self.filtered_data = self.all_data.copy()
            return
        self.filtered_data = []
        for item in self.all_data:
            all_fields = f"{item['country']} {item['city']} {item['rtsp']} {item['user']} {item['password']} {item['lalo']} {item['asn']} {item['sys_org']} {item['network']}".lower()
            if kw in all_fields:
                self.filtered_data.append(item)

class UnifiedEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bloodcat Editor")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(script_dir, "location", "ico.png")
        if os.path.isfile(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        else:
            self.setWindowIcon(QIcon.fromTheme("edit-table"))

        self.current_file_type = None
        self.bc_loader = BCDataLoader()  
        self.hik_data = []
        self.hik_headers = []
        self.hik_current_delimiter = ','
        self.hik_geo_cache = {}
        self.hik_geo = Location()  
        self.hik_filtered_data = []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self.do_global_search)
        self.init_ui()
        self.init_style()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        main_content = self.create_main_content()
        main_layout.addWidget(main_content, 1)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Ready | No file loaded")

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setMaximumWidth(280)
        sidebar.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 8px; }")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        title_label = QLabel("Operation Panel")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(8)
        self.btn_import = QPushButton("Import File")
        self.btn_import.clicked.connect(self.import_file)
        self.btn_import.setMinimumHeight(40)
        file_layout.addWidget(self.btn_import)
        self.btn_export = QPushButton("Export Selected")
        self.btn_export.clicked.connect(self.export_selected)
        self.btn_export.setMinimumHeight(40)
        self.btn_export.setEnabled(False)
        file_layout.addWidget(self.btn_export)
        layout.addWidget(file_group)
        select_group = QGroupBox("Selection Operations")
        select_layout = QVBoxLayout(select_group)
        select_layout.setSpacing(8)
        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_select_all.setEnabled(False)
        btn_layout.addWidget(self.btn_select_all)
        self.btn_invert = QPushButton("Invert")
        self.btn_invert.clicked.connect(self.invert_selection)
        self.btn_invert.setEnabled(False)
        btn_layout.addWidget(self.btn_invert)
        select_layout.addLayout(btn_layout)
        btn_layout2 = QHBoxLayout()
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_selection)
        self.btn_clear.setEnabled(False)
        btn_layout2.addWidget(self.btn_clear)
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setEnabled(False)
        btn_layout2.addWidget(self.btn_delete)
        select_layout.addLayout(btn_layout2)
        layout.addWidget(select_group)
        extra_group = QGroupBox("Geographical location")
        extra_layout = QVBoxLayout(extra_group)
        extra_layout.setSpacing(8)
        self.btn_map = QPushButton("View Map")
        self.btn_map.clicked.connect(self.open_map)
        self.btn_map.setEnabled(False)
        self.btn_map.setMinimumHeight(40)
        extra_layout.addWidget(self.btn_map)
        layout.addWidget(extra_group)
        layout.addStretch()
        return sidebar

    def create_main_content(self):
        content = QFrame()
        content.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 8px; }")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        search_bar = QHBoxLayout()
        self.le_search = QLineEdit()
        self.le_search.setPlaceholderText("Global search (all fields) - type to match automatically...")
        self.le_search.textChanged.connect(self.on_search_text_changed)
        search_bar.addWidget(self.le_search, 1)
        self.btn_clear_search = QPushButton("Clear Search")
        self.btn_clear_search.clicked.connect(self.clear_search)
        search_bar.addWidget(self.btn_clear_search)
        layout.addLayout(search_bar)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.cellDoubleClicked.connect(self.show_row_details)
        self.table.itemChanged.connect(self._on_table_item_changed)
        layout.addWidget(self.table, 1)

        return content

    def _on_table_item_changed(self, item):
        try:
            if item.column() == 0:
                od = item.data(Qt.UserRole)
                if isinstance(od, dict):
                    od['selected'] = (item.checkState() == Qt.Checked)
        except Exception:
            pass

    def init_style(self):
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 12px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f1f1;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
                outline: none;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #e0e0e0;
            }
        """)

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", os.getcwd(),
            "Supported Files (*.bc *.json *.csv);;BC Files (*.bc *.json);;CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.bc', '.json']:
            self.import_bc_file(file_path)
        elif file_ext in ['.csv']:
            self.import_hik_file(file_path)
        else:
            QMessageBox.warning(self, "Unsupported File", f"File type {file_ext} is not supported")
            return

    def import_bc_file(self, file_path):
        if not self.bc_loader:
            QMessageBox.critical(self, "Error", "BC loader is not available")
            return
        if self.bc_loader.import_bc_file(file_path):
            self.current_file_type = 'bc'
            self.hik_filtered_data = []
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
            self.enable_buttons(True)
            self.btn_map.setEnabled(True)
            self.update_status(f"Loaded BC file: {os.path.basename(file_path)} | {len(self.bc_loader.all_data)} records")

    def import_hik_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            delimiter = ',' if text.count(',') >= text.count('\t') else '\t'
            self.hik_current_delimiter = delimiter
            rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
            if not rows:
                QMessageBox.warning(self, "Empty File", "The selected file contains no data")
                return
            self.hik_headers = [h.strip() for h in rows[0]]
            self.hik_data.clear()
            self.hik_filtered_data.clear()
            self.hik_geo_cache.clear()
            for r in rows[1:]:
                r += [''] * (len(self.hik_headers) - len(r))
                od = OrderedDict(zip(self.hik_headers, r))
                ip_candidate = ''
                if len(r) >= 3 and r[1].strip() == '0':
                    ip_candidate = self.extract_ip(r[2])
                if not ip_candidate:
                    for k in ['IP','ip','Address','address','Host','host']:
                        if k in od and od[k].strip():
                            ip_candidate = self.extract_ip(od[k].strip())
                            break
                geo_full = self.fetch_geo_full(ip_candidate) if self.hik_geo else {}
                od['__geo_country'] = geo_full.get('country', '') if isinstance(geo_full, dict) else ''
                od['__geo_full'] = geo_full
                od['selected'] = False
                self.hik_data.append(od)
            self.hik_filtered_data = self.hik_data.copy()
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
            self.current_file_type = 'hik'
            self.enable_buttons(True)
            self.btn_map.setEnabled(True)
            self.update_status(f"Loaded Hik file: {os.path.basename(file_path)} | {len(self.hik_data)} records")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import Hik file: {str(e)}")

    def _populate_hik_table_chunked(self, rows, chunk_size=200):
        self.table.setRowCount(0)
        self.table.setColumnCount(2 + len(self.hik_headers))
        self.table.setHorizontalHeaderLabels(['Sel', 'Country'] + self.hik_headers)

        self._chunk_rows = rows
        self._chunk_index = 0
        self.table.setUpdatesEnabled(False)

        def process_chunk():
            start = self._chunk_index
            end = min(start + chunk_size, len(self._chunk_rows))
            self.table.blockSignals(True)
            for r in range(start, end):
                od = self._chunk_rows[r]
                row = self.table.rowCount()
                self.table.insertRow(row)
                check_item = QTableWidgetItem()
                check_item.setFlags(check_item.flags() | Qt.ItemIsUserCheckable)
                check_item.setCheckState(Qt.Checked if od.get("selected", False) else Qt.Unchecked)
                check_item.setData(Qt.UserRole, od)
                self.table.setItem(row, 0, check_item)

                country_item = QTableWidgetItem(od.get('__geo_country', ''))
                country_item.setFlags(country_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, country_item)

                for c, h in enumerate(self.hik_headers, start=2):
                    it = QTableWidgetItem(od.get(h, ''))
                    it.setData(Qt.UserRole, od)
                    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, c, it)
            self.table.blockSignals(False)
            self._chunk_index = end
            if self._chunk_index % (chunk_size * 2) == 0 or self._chunk_index == len(self._chunk_rows):
                self.table.resizeColumnsToContents()

            if self._chunk_index < len(self._chunk_rows):
                QTimer.singleShot(10, process_chunk)
            else:
                self.table.setUpdatesEnabled(True)
                self.table.resizeColumnsToContents()
                self.table.horizontalHeader().setStretchLastSection(True)

        process_chunk()

    def _populate_bc_table_chunked(self, rows, chunk_size=300):
        headers = ["Select", "Country", "City", "RTSP", "User", "Pass",
                   "LatLon", "ASN", "Org", "Network"]
        self.table.setRowCount(0)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self._chunk_rows = rows
        self._chunk_index = 0
        self.table.setUpdatesEnabled(False)

        def process_chunk():
            start = self._chunk_index
            end = min(start + chunk_size, len(self._chunk_rows))
            self.table.blockSignals(True)
            for r in range(start, end):
                item = self._chunk_rows[r]
                row = self.table.rowCount()
                self.table.insertRow(row)
                check_item = QTableWidgetItem()
                check_item.setFlags(check_item.flags() | Qt.ItemIsUserCheckable)
                check_item.setCheckState(Qt.Checked if item.get("selected", False) else Qt.Unchecked)
                check_item.setData(Qt.UserRole, item)
                self.table.setItem(row, 0, check_item)

                cells = [
                    item.get("country", ""),
                    item.get("city", ""),
                    item.get("rtsp", ""),
                    item.get("user", ""),
                    item.get("password", ""),
                    item.get("lalo", ""),
                    str(item.get("asn", "")),
                    item.get("sys_org", ""),
                    item.get("network", "")
                ]
                for col_offset, value in enumerate(cells, start=1):
                    twi = QTableWidgetItem(value)
                    twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, col_offset, twi)
            self.table.blockSignals(False)
            self._chunk_index = end
            if self._chunk_index % (chunk_size * 2) == 0 or self._chunk_index == len(self._chunk_rows):
                self.table.resizeColumnsToContents()

            if self._chunk_index < len(self._chunk_rows):
                QTimer.singleShot(10, process_chunk)
            else:
                self.table.setUpdatesEnabled(True)
                self.table.resizeColumnsToContents()
                self.table.horizontalHeader().setStretchLastSection(True)

        process_chunk()

    def export_selected(self):
        if not self.current_file_type:
            QMessageBox.warning(self, "No Data", "Please import a file first")
            return
        if self.current_file_type == 'bc':
            selected = [i for i in self.bc_loader.all_data if i.get("selected", False)]
            if not selected:
                QMessageBox.warning(self, "No Selection", "No BC records selected")
                return
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save BC File", "export.bc", "BC Files (*.bc *.json)"
            )
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("")
                    for item in selected:
                        self.bc_loader.cam.save_info(
                            rtsp_url=item.get("rtsp", ""),
                            ip_data=item,
                            path_file=file_path,
                            ver=True
                        )
                    QMessageBox.information(self, "Success", f"Exported {len(selected)} BC records")
                    self.update_status(f"Exported {len(selected)} BC records to {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export BC file: {str(e)}")
        elif self.current_file_type == 'hik':
            selected = [i for i in self.hik_data if i.get("selected", False)]
            if not selected:
                QMessageBox.warning(self, "No Selection", "No Hik records selected")
                return
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "export.csv", "CSV Files (*.csv)")
            if file_path:
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f, delimiter=self.hik_current_delimiter)
                        writer.writerow(self.hik_headers)
                        for od in selected:
                            writer.writerow([od.get(h, '') for h in self.hik_headers])
                    QMessageBox.information(self, "Success", f"Exported {len(selected)} Hik records")
                    self.update_status(f"Exported {len(selected)} Hik records to {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export Hik file: {str(e)}")

    def select_all(self):
        if self.current_file_type == 'bc':
            for item in self.bc_loader.filtered_data:
                item["selected"] = True
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
        elif self.current_file_type == 'hik':
            for item in self.hik_filtered_data:
                item["selected"] = True
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
        self.update_status("All visible records selected")

    def invert_selection(self):
        if self.current_file_type == 'bc':
            for item in self.bc_loader.filtered_data:
                item["selected"] = not item.get("selected", False)
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
        elif self.current_file_type == 'hik':
            for item in self.hik_filtered_data:
                item["selected"] = not item.get("selected", False)
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
        self.update_status("Selection inverted (visible records only)")

    def clear_selection(self):
        if self.current_file_type == 'bc':
            for item in self.bc_loader.filtered_data:
                item["selected"] = False
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
        elif self.current_file_type == 'hik':
            for item in self.hik_filtered_data:
                item["selected"] = False
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
        self.update_status("Selection cleared (visible records only)")

    def delete_selected(self):
        if not self.current_file_type:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure to delete selected records? This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        if self.current_file_type == 'bc':
            before = len(self.bc_loader.all_data)
            self.bc_loader.all_data = [i for i in self.bc_loader.all_data if not i.get("selected", False)]
            self.bc_loader.global_filter_data(self.le_search.text())
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
            deleted = before - len(self.bc_loader.all_data)
            self.update_status(f"Deleted {deleted} BC records")
        elif self.current_file_type == 'hik':
            before = len(self.hik_data)
            self.hik_data = [i for i in self.hik_data if not i.get("selected", False)]
            self.hik_filtered_data = [i for i in self.hik_filtered_data if not i.get("selected", False)]
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
            deleted = before - len(self.hik_data)
            self.update_status(f"Deleted {deleted} Hik records")
        QMessageBox.information(self, "Deleted", f"Successfully deleted {deleted} records")

    def open_map(self):
        if self.current_file_type not in ('hik', 'bc') or not WEB_ENGINE_AVAILABLE:
            QMessageBox.warning(self, "Unavailable", "Map function is available for BC or Hikvision CSV data with PyQtWebEngine installed")
            return
        markers_data = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_url = ""
        for icon_file in ['location/color_1.png', 'location/ico.png']:
            icon_path = os.path.join(script_dir, icon_file)
            if os.path.isfile(icon_path):
                icon_url = QUrl.fromLocalFile(icon_path).toString()
                break
        if self.current_file_type == 'hik':
            source = self.hik_filtered_data
            headers = self.hik_headers
            for od in source:
                if not od.get('__geo_full') or not od.get('__geo_full').get('lalo'):
                    continue
                ip = ''
                if len(headers) >= 3 and od.get(headers[1], '').strip() == '0':
                    ip = self.extract_ip(od.get(headers[2], ''))
                if not ip:
                    for k in ['IP','ip','Address','address','Host','host','Name']:
                        if k in od and od[k].strip():
                            ip = self.extract_ip(od[k].strip())
                            break
                if not ip:
                    ip = f"row_{id(od)}"
                geo = od.get('__geo_full') or {}
                lalo = geo.get('lalo') or geo.get('latlng') or ''
                if isinstance(lalo, (list, tuple)) and len(lalo) >= 2:
                    lalo = f"{lalo[0]},{lalo[1]}"
                markers_data[ip] = {
                    'lalo': str(lalo),
                    'asn': geo.get('asn',''),
                    'sys_org': geo.get('sys_org','') or od.get('User Name','') or '',
                    'network': geo.get('network',''),
                    'rtsp': od.get('Address','') or '',
                    'icon': icon_url
                }
        else:
            source = self.bc_loader.filtered_data
            for idx, item in enumerate(source):
                lalo = item.get('lalo', '')
                if not lalo:
                    continue
                ip = item.get('rtsp') or f"bc_{idx}"
                markers_data[ip] = {
                    'lalo': str(lalo),
                    'asn': item.get('asn',''),
                    'sys_org': item.get('sys_org',''),
                    'network': item.get('network',''),
                    'rtsp': item.get('rtsp',''),
                    'icon': icon_url
                }
        if not markers_data:
            QMessageBox.information(self, "No Data", "No geographic data available for mapping")
            return
        dlg = MapDialog(self, markers_data)
        dlg.exec_()

    def on_search_text_changed(self):
        if not self.current_file_type:
            return
        self.search_timer.start()

    def do_global_search(self):
        keyword = self.le_search.text().strip()
        if self.current_file_type == 'bc':
            self.bc_loader.global_filter_data(keyword)
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
            match_count = len(self.bc_loader.filtered_data)
        elif self.current_file_type == 'hik':
            self.hik_global_filter_data(keyword)
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
            match_count = len(self.hik_filtered_data)
        else:
            return
        if keyword:
            self.update_status(f"Global search matched {match_count} records (keyword: '{keyword}')")
        else:
            self.update_status("Search cleared - showing all records")

    def hik_global_filter_data(self, keyword):
        kw = keyword.lower().strip()
        if not kw:
            self.hik_filtered_data = self.hik_data.copy()
            return
        self.hik_filtered_data = []
        for item in self.hik_data:
            all_fields = []
            all_fields.append(item.get('__geo_country', ''))
            for h in self.hik_headers:
                all_fields.append(str(item.get(h, '')))
            all_fields_str = ' '.join(all_fields).lower()
            if kw in all_fields_str:
                self.hik_filtered_data.append(item)

    def clear_search(self):
        self.le_search.clear()
        if self.current_file_type == 'bc':
            self.bc_loader.global_filter_data("")
            self._populate_bc_table_chunked(self.bc_loader.filtered_data, chunk_size=300)
        elif self.current_file_type == 'hik':
            self.hik_filtered_data = self.hik_data.copy()
            self._populate_hik_table_chunked(self.hik_filtered_data, chunk_size=200)
        self.update_status("Search cleared - showing all records")

    def show_row_details(self, row, col):
        if self.current_file_type != 'hik':
            return
        item = self.table.item(row, 2)
        if not item:
            return
        od = item.data(Qt.UserRole)
        if not isinstance(od, dict):
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Record")
        dlg.setMinimumWidth(500)
        layout = QVBoxLayout(dlg)
        country = od.get('__geo_country', '')
        if country:
            geo_label = QLabel(f"Country: {country}")
            geo_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(geo_label)
        form_layout = QFormLayout()
        edits = {}
        for h in self.hik_headers:
            le = QLineEdit(od.get(h, ''))
            edits[h] = le
            form_layout.addRow(h, le)
        layout.addLayout(form_layout)
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)
        if dlg.exec_():
            for h, le in edits.items():
                od[h] = le.text()
            ip_candidate = ''
            if len(self.hik_headers) >= 3:
                ip_candidate = self.extract_ip(od.get(self.hik_headers[2], ''))
            if not ip_candidate:
                for k in ['IP','ip','Address','address']:
                    if k in od and od[k].strip():
                        ip_candidate = self.extract_ip(od[k].strip())
                        break
            if ip_candidate and self.hik_geo:
                geo_full = self.fetch_geo_full(ip_candidate)
                od['__geo_full'] = geo_full
                od['__geo_country'] = geo_full.get('country', '')
            self.do_global_search()
            self.update_status("Record updated successfully")

    def enable_buttons(self, enabled):
        self.btn_export.setEnabled(enabled)
        self.btn_select_all.setEnabled(enabled)
        self.btn_invert.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)

    def update_status(self, message):
        self.status_bar.showMessage(message, 5000)

    def extract_ip(self, text):
        if not text:
            return ''
        m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', text.strip())
        return m.group(1) if m else ''

    def is_public_ip(self, ip):
        try:
            return ipaddress.ip_address(ip).is_global
        except Exception:
            return False

    def fetch_geo_full(self, ip):
        if not self.hik_geo or not ip:
            return {}
        clean_ip = self.extract_ip(ip)
        if not clean_ip or not self.is_public_ip(clean_ip):
            return {}
        if clean_ip in self.hik_geo_cache:
            return self.hik_geo_cache[clean_ip]
        try:
            data = self.hik_geo.get(clean_ip)
            if isinstance(data, dict):
                self.hik_geo_cache[clean_ip] = data
                return data
        except Exception as e:
            print(f"Geo lookup failed for {clean_ip}: {e}")
        self.hik_geo_cache[clean_ip] = {}
        return {}

def main():
    print(LOGO)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("BloodCat Editor")
    app.setApplicationVersion(VERSION)
    editor = UnifiedEditor()
    editor.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
