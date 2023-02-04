# cityseer-qgis

QGIS plugin for cityseer-api

## Development

1. Install `brew` packages per `brew install qt5 pyqt pdm qgis`
2. Install pythong packages per `pdm install`
3. Add a `.env` file in `vscode` adding QGIS to the python path (per system QGIS location):

```bash
PYTHONPATH="${env:PYTHONPATH}:/Applications/Qgis.app/Contents/Resources/python/plugins:/Applications/Qgis.app/Contents/Resources/python"
```

4. Create a softlink from the dev plugin folder to the QGIS plugins directory, this is system specific, e.g.:

```bash
ln -s /Users/gareth/dev/benchmark-urbanism/cityseer-qgis/cityseer-qgis /Users/gareth/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins
```

## QGIS plugin config

QGIS doesn't yet support automatic third party package installation, so `cityseer` has to be installed manually for the time being:

```bash
/Applications/QGIS.app/Contents/MacOS/bin/pip install cityseer
```
