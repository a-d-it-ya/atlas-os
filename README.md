# ⬡ Shakti OS

Autonomous border surveillance and command platform for India's armed forces.

---

## What It Does

- Ingests data from any sensor — radar, thermal, acoustic
- Converts every detection into a standardised **Entity** object
- Displays all tracks live on a map of the target sector
- Lets operators draw **restricted zones** on the map
- Fires an alert the moment a hostile track enters a zone

---

## Run It

```bash
pip install websockets
```

```bash
# Terminal 1
python simulator/fake_radar.py

# Terminal 2
python core/shakti_core.py

# Terminal 3 — open in browser
frontend/index.html
```

---

## Structure

```
shakti-os/
├── core/
│   └── shakti_core.py      # Entity pipeline
├── simulator/
│   └── fake_radar.py       # Simulated radar
└── frontend/
    └── index.html          # Operator map
```

---

Built by a 23-year-old. Day 1 was tonight.
