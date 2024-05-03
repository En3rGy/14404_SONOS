# SONOS Speaker (14404)

## Voraussetzungen
HSL 2.0.4

## Installation
Die .hslz Datei mit dem Gira Experte importieren. Das Logikmodul ist dann in der Rubrik "Datenaustausch" verfügbar.

## Eingänge

| Nr. | Eingang      | Initwert | Beschreibung                    |
|-----|--------------|----------|---------------------------------|
| 1   | Speaker IP   |          | IP des jew. SONOS Lautsprechers |
| 2   | Volume       | 0        | Lautstärke in %                 | 
| 3   | Play         | 0        | 1 Startet die Wiedergabe        |
| 4   | Pause        | 0        | 1 kommandiert "Pause"           | 
| 5   | Previous     | 0        | 1 spielt den vorherigen Track   |
| 6   | Next         | 0        | 1 spielt den nächsten Track     |
| 7   | Playlist     |          | Name der Sonos Playlist         |
| 8   | Radio        |          | Name des Radiosenders           |
| 9   | Join RINCON  |          |                                 |


## Ausgänge
Alle Ausgänge sind Send-by-Change ausgeführt.

| Nr. | Ausgang | Initwert | Beschreibung                                                    |
|-----|---------|----------|-----------------------------------------------------------------|
| 1   | Debug   | 0        | Success = 1 / Failure = 0 für die Ausführung der letzten Aktion |


## Sonstiges

- Neuberechnung beim Start: Nein
- Baustein ist remanent: Nein
- Interne Bezeichnung: 14404

### Change Log

- v00.06: Initial

### Open Issues / Known Bugs



### Support

Für Fehlermeldungen oder Feature-Wünsche, bitte [github issues](https://github.com/En3rGy/14401_FeiertageFerien/issues) nutzen.
Fragen am besten als Thread im [knx-user-forum.de](https://knx-user-forum.de) stellen. Dort finden sich ggf. bereits Diskussionen und Lösungen.

## Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14401_FeiertageFerien).

### Entwicklungsumgebung

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python *markdown* module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)

## Anforderungen


## Software Design Description



## Validierung und Verifikation

- Unit Tests

## Lizenz

Copyright 2024 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
