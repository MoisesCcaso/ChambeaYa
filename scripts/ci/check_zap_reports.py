#!/usr/bin/env python3
"""Fail the CI gate when either ZAP Baseline report contains a High alert."""

import json
import sys
from pathlib import Path


def alerts(value):
    if isinstance(value, dict):
        if "riskcode" in value and ("alert" in value or "pluginid" in value):
            yield value
        for child in value.values():
            yield from alerts(child)
    elif isinstance(value, list):
        for child in value:
            yield from alerts(child)


def main(paths):
    high_alerts = []
    for filename in paths:
        path = Path(filename)
        if not path.is_file():
            print(f"Falta el reporte ZAP: {path}", file=sys.stderr)
            return 1
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"No se pudo leer el reporte ZAP {path}: {error}", file=sys.stderr)
            return 1

        for alert in alerts(report):
            if str(alert.get("riskcode", "")) == "3":
                high_alerts.append((path.name, alert))

    for report_name, alert in high_alerts:
        print(
            f"HIGH en {report_name}: {alert.get('alert', 'Alerta ZAP')} "
            f"({alert.get('url', 'sin URL')})",
            file=sys.stderr,
        )
    if high_alerts:
        print(f"Gate ZAP rechazado: {len(high_alerts)} alerta(s) High.", file=sys.stderr)
        return 1

    print("Gate ZAP aprobado: no se encontraron alertas High.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <reporte.json> [reporte.json ...]", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
