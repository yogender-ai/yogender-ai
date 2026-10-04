# Profile Architecture & Automation Pipeline 🐺

This repository powers the dynamic GitHub profile presence for [@yogender-ai](https://github.com/yogender-ai).

---

## 🎨 Asset Generation (`.github/scripts/build_assets.py`)
- Generates 6 project showcase cards:
  1. `dsa-journey.svg` (Top centerpiece)
  2. `newsintel.svg`
  3. `cloud-command.svg`
  4. `particle-gravity.svg`
  5. `knn-cat-dog.svg`
  6. `financeinsight.svg`
- Generates `dsa.svg` tracking live LeetCode stats (276 solved, 74d streak).
- Builds `terminal.svg`, the deep-space `hero.svg` — a new sky every day (7 rotating scenes: ringed giant, black hole, eclipse, ice world, spiral galaxy, binary suns, red planet; nebula, stars and colours seeded by the UTC date; README links it with `?d=<day>` to beat the image cache; preview another day with `HERO_DAY=<ordinal>`), `orbits.svg` (tech stack as a solar system), `launch.svg` (warp-speed rocket divider), starry section headers with orbiting planets and the planet-horizon `footer.svg`.

---

## 🔄 Automated CI Workflows
- **Contribution Snake Animation** (`.github/workflows/snake.yml`): Runs every 12 hours to regenerate the contribution graph grid and pushes output to the `output` branch.
- **Dependabot** (`.github/dependabot.yml`): Automatically checks and creates pull requests for GitHub Actions version bumps.
