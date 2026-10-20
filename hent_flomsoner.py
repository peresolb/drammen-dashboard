"""Hent NVE-flomsoner for Drammen som GeoJSON, ett lag per gjentaksintervall."""
import json
from pathlib import Path

import requests

SERVICE_URL = "https://kart.nve.no/enterprise/rest/services/Flomsoner2/MapServer"
DRAMMEN_BBOX = (9.95, 59.63, 10.45, 59.85)
LAYER_PREFIXES = ("Flomsone_", "FlomsoneAnalyseomraade")
PAGE_SIZE = 1000


def flood_zone_layers(session: requests.Session) -> list[dict]:
    """Return the flood zone layers and the mapped-area layer, looked up by name."""
    response = session.get(SERVICE_URL, params={"f": "json"}, timeout=30)
    response.raise_for_status()
    return [layer for layer in response.json()["layers"]
            if layer["name"].startswith(LAYER_PREFIXES)]


def _spatial_params(bbox: tuple[float, float, float, float]) -> dict:
    """Return query parameters that select features intersecting a WGS84 bbox."""
    return {
        "where": "1=1",
        "geometry": ",".join(map(str, bbox)),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
    }


def fetch_layer(session: requests.Session, layer_id: int,
                bbox: tuple[float, float, float, float]) -> list[dict]:
    """Return every feature in one layer that intersects bbox, in WGS84."""
    url = f"{SERVICE_URL}/{layer_id}/query"
    count_params = {**_spatial_params(bbox), "returnCountOnly": "true", "f": "json"}
    total = session.get(url, params=count_params, timeout=60).json()["count"]

    features: list[dict] = []
    for offset in range(0, total, PAGE_SIZE):
        params = {
            **_spatial_params(bbox),
            "outFields": "*",
            "outSR": 4326,
            "orderByFields": "OBJECTID",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
            "f": "geojson",
        }
        response = session.get(url, params=params, timeout=120)
        response.raise_for_status()
        features.extend(response.json()["features"])
    return features


def main() -> None:
    """Save each layer with data for Drammen to its own GeoJSON file."""
    out_dir = Path("flomsoner_drammen")
    out_dir.mkdir(exist_ok=True)
    with requests.Session() as session:
        for layer in flood_zone_layers(session):
            features = fetch_layer(session, layer["id"], DRAMMEN_BBOX)
            print(f"{layer['name']:<30} {len(features)} flater")
            if features:
                collection = {"type": "FeatureCollection", "features": features}
                (out_dir / f"{layer['name']}.geojson").write_text(json.dumps(collection))


if __name__ == "__main__":
    main()
