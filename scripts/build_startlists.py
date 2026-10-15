#!/usr/bin/env python3
"""Validate a semicolon-separated V85 start list and produce static JSON."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "startlistor.csv"
target = ROOT / "data" / "startlistor.json"
fields = ["avdelning", "nummer", "hast", "kusk", "tranare", "spar"]
with source.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle, delimiter=";")
    if reader.fieldnames != fields:
        raise SystemExit("Fel CSV-kolumner. Förväntar: " + ";".join(fields))
    horses = []
    seen = set()
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise SystemExit("Fel antal kolumner")
        leg = int(row["avdelning"])
        number = int(row["nummer"])
        post = int(row["spar"])
        if not 1 <= leg <= 8 or not 1 <= number <= 99 or not 0 <= post <= 99:
            raise SystemExit("Ogiltig avdelning, nummer eller spår")
        if not row["hast"].strip() or (leg, number) in seen:
            raise SystemExit("Tomt hästnamn eller dubblett")
        seen.add((leg, number))
        horses.append({
            "leg": leg, "number": number, "horse": row["hast"].strip(),
            "driver": row["kusk"].strip(), "trainer": row["tranare"].strip(), "post": post
        })
    if len(horses) > 500:
        raise SystemExit("För många hästar")
payload = {
    "schema": 1,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source": "CSV uppladdad av användaren – ej officiellt verifierad",
    "horses": sorted(horses, key=lambda h: (h["leg"], h["number"]))
}
target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Validerade {len(horses)} hästar")
