# drammen-dashboard

## Flomsoner fra NVE

`hent_flomsoner.py` laster ned NVE sine flomsoner for Drammen-området fra
karttjenesten `Flomsoner2` på `kart.nve.no`. Hvert gjentaksintervall blir én
GeoJSON-fil (WGS84) i mappa `flomsoner_drammen/`.

```bash
pip install -r requirements.txt
python hent_flomsoner.py
```
