# Decision-Support Tool — Food Donation Allocation

Project built in preparation for the **BCG Platinion Hackathon 2026** (theme: *Fighting World Hunger*).

## Business problem

When an NGO or food bank has a limited stock of donations and needs to
decide **where to start**, the decision is often made on gut feeling or a
first-come-first-served basis. This project proposes a simple and
transparent method to prioritize which regions to help, taking several
criteria into account at once rather than just one.

## Approach

1. **Business framing**: 4 criteria chosen to prioritize food aid:
   - the region's food insecurity rate
   - days left before the local stock expires (urgency)
   - stock already on hand (the less there is, the more urgent the need)
   - distance from the distribution hub (logistics factor)
2. **Normalization** of each criterion between 0 and 1 (min-max scaling).
3. **Weighted priority score** to rank the regions.
4. **Text recommendations** generated automatically from the ranking.

### Why this default weighting?

| Criterion | Weight | Rationale |
|---|---|---|
| Food insecurity rate | 40% | The core of the problem: aid should first follow the population's actual need. |
| Days until expiry | 25% | A local stock about to expire creates short-term urgency, even if the overall need is lower. |
| Stock on hand | 20% | Avoids over-supplying a region that's already well covered. |
| Distance to hub | 15% | A real logistics factor, but deliberately secondary: we don't want to ignore a region in need just because it's far away. |

These weights are **a deliberate business choice, not a universal truth**
— which is why `sensitivity_analysis.py` tests 2 other strategies
(urgency-first, logistics-first) and shows how the ranking is affected.

## Two approaches, both kept on purpose

- **`prioritize_donations.py`** (V1): answers "where should we start?" —
  a simple ranking, on fictional data. Educational starting point.
- **`allocate_stock.py`** (V2): answers "how much should we send to each
  region?" — a real optimization problem under constraints (total stock,
  per-region capacity), on real data (HCP population and poverty figures).

## Project structure

```
food-aid-project-en/
├── data/
│   ├── regions.csv           # first version, fully fictional data
│   ├── regions_real.csv      # real data (population, poverty) + fictional operational data
│   └── SOURCES.md            # exact provenance of every column
├── src/
│   ├── scoring.py             # scoring logic (normalization, weighting, validation)
│   └── optimization.py        # optimal allocation of a limited stock (linear programming, PuLP)
├── tests/
│   ├── test_scoring.py        # scoring tests
│   └── test_optimization.py   # optimization tests
├── results/                   # generated outputs (CSV + charts)
├── prioritize_donations.py    # V1: simple region ranking (fictional data)
├── allocate_stock.py          # V2: optimal allocation under constraints (real data)
├── sensitivity_analysis.py    # compares 3 weighting strategies
├── app.py                     # interactive Streamlit interface
├── requirements.txt
└── README.md
```

The scoring logic (`src/scoring.py`) is kept separate from the execution
scripts so it can be tested independently and reused elsewhere (an API, a
notebook...).

## Data

The `data/regions_real.csv` file contains Morocco's 12 regions with
**real population and poverty indicators**, and **fictional but realistic
operational indicators** (distance, stock, expiry). See `data/SOURCES.md`
for the exact provenance of every column.

## Usage

```bash
pip install -r requirements.txt

# V1: simple ranking (fictional data)
python prioritize_donations.py

# V2: optimal allocation under constraints (real data)
python allocate_stock.py --stock 300

# Compare 3 weighting strategies
python sensitivity_analysis.py

# Interactive interface
streamlit run app.py

# Tests
python -m pytest tests/ -v
```

## Limitations and possible improvements

- Population and poverty data are real; the operational data (stock,
  distance, expiry) is fictional, since it isn't publicly available (see
  `data/SOURCES.md`).
- The model doesn't account for real logistics constraints (truck
  capacity, passable roads, seasonality).
- Text recommendations are generated with simple rules; they could be
  enriched with a language model (e.g. Claude) to produce richer
  summaries for field teams.

## Author

Yassmine Ait Bentaleb — Engineering student at INPT, Innovation & AMOA
track. Profile focused on business analysis, data governance, and
applied AI solutions.
