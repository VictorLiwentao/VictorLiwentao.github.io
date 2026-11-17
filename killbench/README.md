# KillBench

A benchmark of things that kill people, with AI included for scale. Live at
<https://victorliwentao.github.io/killbench/>.

Three tracks:

- **Deaths per year**: tobacco, alcohol, cars, falls, malaria, drowning, guns, snakes, knives, rabies, selfies, AI (2025) and sharks.
- **All-time totals**: smallpox, tobacco, Mao, Hitler, Stalin, Pol Pot, the atomic bombs, Boeing MCAS, selfies, AI and industrial robots, plus AI's expected value under the median researcher forecast (a forecast, not a count).
- **Results by system**: deaths linked to each AI system, confirmed and alleged.

The page lets the reader switch between three AI counting rules (confirmed 5, confirmed or alleged 44, everything any list has 108) and between a log and a linear scale.

## Files

- `data/killbench.json`: every figure, range, note and source. Edit this to update the site.
- `scripts/template.html`: the page (HTML, CSS, JS).
- `scripts/build.py`: writes `index.html` from the two files above. Run `python3 scripts/build.py`.
- `fonts/`: Doto and IBM Plex (SIL Open Font License 1.1), self-hosted.

## Counting rules for AI

- **Confirmed**: a court, coroner, regulator or accident investigator found the system caused or contributed to the death.
- **Alleged**: blamed on a named AI system in a lawsuit, an open investigation, or by at least two news organisations.
- **Everything any list has**: Wikipedia's chatbot list (39) + tesladeaths.com Autopilot/FSD deaths (65) + Uber (1) + openpilot (2) + nH Predict (1).

Counts are a snapshot from 15–16 November 2026 of hasaikilledanyone.com, Wikipedia's "Deaths linked to chatbots" and tesladeaths.com.
AI-assisted military targeting is not scored because no death count can be attributed to the software.
