[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)
# SONOS Speaker (14404)

## Beschreibung
Logikbaustein zur Steuerung von SONOS-Lautsprechern.

## Installation
Die .hslz Datei mit dem Gira Experte importieren. Das Logikmodul ist dann in der Rubrik "Datenaustausch" verfügbar.

## Eingänge

| Nr. | Eingang              | Initwert | Beschreibung                                                                                                                     |
|-----|----------------------|----------|----------------------------------------------------------------------------------------------------------------------------------|
| 1   | Speaker RINCON       |          | Check the modules section on HS-Debug page to identify your speakers RINCON. Shourl be something like `RINCON_123456789ABCD1400` |
| 2   | Volume               | 0        | Lautstärke in %                                                                                                                  | 
| 3   | Play (1) / Pause (0) | 0        | 1 Startet die Wiedergabe, 0 passiert sie                                                                                         |
| 4   | Previous             | 0        | 1 spielt den vorherigen Track                                                                                                    |
| 5   | Next                 | 0        | 1 spielt den nächsten Track                                                                                                      |
| 6   | Playlist             |          | Name der Sonos Playlist                                                                                                          |
| 7   | Radio                |          | Name des Radiosenders                                                                                                            |
| 8   | Join RINCON          |          |                                                                                                                                  |


## Ausgänge
Alle Ausgänge sind Send-by-Change ausgeführt.

| Nr. | Ausgang | Initwert | Beschreibung                                                                                                                                                                      |
|-----|---------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | Debug   | 0        | For debugging during development only. Will output the sum of all received http return codes if `self.debugging = True`. This can only be set within the development environment. |


## Sonstiges

- Neuberechnung beim Start: Nein
- Baustein ist remanent: Nein
- Interne Bezeichnung: 14404

### Change Log

See [release notes](https://github.com/En3rGy/14404_SONOS/releases)

### Open Issues / Known Bugs
x

### Support

Für Fehlermeldungen oder Feature-Wünsche, bitte [github issues](https://github.com/En3rGy/14404_SONOS/issues) nutzen.
Fragen am besten als Thread im [knx-user-forum.de](https://knx-user-forum.de) stellen. Dort finden sich ggf. bereits Diskussionen und Lösungen.

## Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14404_SONOS).

### Entwicklungsumgebung

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python *markdown* module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)

### Anforderungen
x

### Software Design Description
x

### Validierung und Verifikation

- Unit Tests

## Lizenz

Copyright 2024 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
