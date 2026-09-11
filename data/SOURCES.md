# Data provenance — `regions_real.csv`

Full transparency on what is real and what is estimated, column by column.

| Column | Source | Status |
|---|---|---|
| `region` | Official breakdown of Morocco's 12 regions | Real |
| `population` | HCP (Haut-Commissariat au Plan) — General Population and Housing Census (RGPH) 2024 | **Real**, official figures published November 7, 2024 |
| `food_insecurity_rate_pct` (proxy: multidimensional poverty rate) | HCP — "Mapping of multidimensional poverty: territorial landscape and dynamics" (2024) | **Real for 6 regions** explicitly cited in the publication (Béni Mellal-Khénifra 9.8% ; Fès-Meknès 9.0% ; Oriental 8.4% ; Laâyoune-Sakia El Hamra 2.4% ; Dakhla-Oued Ed-Dahab 2.5% ; national average 6.8%). **Estimated by reasoned interpolation** for the other 6 regions, as the HCP only published the above/below national-average extremes in the press releases available. The full per-region dataset exists in the complete HCP report (not publicly accessible in detail for every region at the time this project was built). |
| `distance_to_hub_km` | Fictional | Not publicly available — internal logistics data specific to each NGO's warehouse location |
| `stock_on_hand_tonnes` | Fictional | Not publicly available — internal stock management data |
| `days_until_expiry` | Fictional | Not publicly available — internal stock management data |

## Why this choice

Using real demographic and poverty data makes the model far more credible
than fully invented numbers, while staying honest about its limits:
operational data (stock, distance, expiry) simply doesn't exist in the
public domain, since it belongs to each humanitarian organization's internal
management. A real deployment of this tool would use the internal data of
the NGO using it for these three columns.

## Sources consulted

- HCP, RGPH 2024 — legal population by region (November 2024)
- HCP, "Mapping of multidimensional poverty: territorial landscape and
  dynamics" (2024)
