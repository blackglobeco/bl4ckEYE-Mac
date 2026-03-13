# BloodCat Map — Web App

A browser-based CCTV camera world map built with Flask + Leaflet.js.

## Run

```bash
python bloodcat_map.py
```

Starts the web server at `http://0.0.0.0:5000`.

## Features

- Dark world map (Leaflet + CARTO dark tiles)
- Camera markers loaded from encrypted `.bc` database files
- Click any marker → popup modal with camera info + live snapshot attempt
- Search cameras by IP, ASN, Network, or Org
- Add/remove remote database URLs (stored in `data/bloodcatmap.conf`)
- Camera counter in top-left
- Local BC file server on port 34713

## Architecture

- **`bloodcat_map.py`** — Flask web server (main entry point)
- **`lib/camlib.py`** — Camera database loader, AES encryption/decryption
- **`lib/location.py`** — GeoIP lookup
- **`lib/log_cat.py`** — Logging helper
- **`data/bloodcatmap.conf`** — JSON list of remote DB URLs
- **`data/global.bc`** — Local encrypted camera database
- **`location/`** — Static assets (color icons, map template)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main map HTML page |
| GET | `/api/data` | Load and return all camera markers as JSON |
| GET | `/api/config` | Get list of remote DB URLs |
| POST | `/api/config` | Add a remote DB URL |
| DELETE | `/api/config` | Remove a remote DB URL |
| GET | `/api/snapshot/<ip>` | Proxy a live snapshot from camera IP |

## Dependencies

- Flask
- requests
- pycryptodome
- geoip2
- aiohttp
