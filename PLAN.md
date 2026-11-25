# Project Plan

## Goal
Analyze public video game data to answer a few practical questions about
what drives ratings, success and release patterns across PC (Steam) and
console exclusives. The finished site is a single project I can point to
as an example of my data cleaning, SQL, Python and visualization work.

## Questions
1. Do console exclusives receive higher critic ratings than multiplatform games?
   Broken down by Nintendo, PlayStation and Xbox.
2. Which exclusive franchises have stayed on top across console generations?
   Measured by generations covered, years active and critic scores over time.
3. What separates successful Steam games from unsuccessful ones?
   Looking at price, genre and tags.
4. Is the release calendar getting more crowded, and do games released in
   busy months perform differently?
5. Live: which games have the most Steam players right now, and how does
   that change by hour and day?

## Data Sources
| Source | Used for | Notes |
|---|---|---|
| IGDB API | Q1, Q2, Q4 | Free. Needs Twitch developer credentials. |
| Steam Games Dataset (FronkonGames, Hugging Face) | Q3, Q4 | Free. Prebuilt from Steam and SteamSpy data. |
| SteamSpy API | Filling gaps in Q3 | Free. Owner counts are estimated ranges. |
| Steam Web API (GetNumberOfCurrentPlayers) | Q5 | Free, no key. Counts Steam players only. |

## Decisions
- No per-game sales comparison across consoles. Nintendo publishes top-seller
  lists, Sony only publishes occasional milestones, and Microsoft does not
  publish sales. Comparing them would not be consistent.
- The franchise question uses IGDB data for all three companies so the
  comparison is measured the same way.
- Live player counts are collected hourly by a scheduled GitHub Action and
  saved to the repo. The site reads the saved file, not the API directly,
  so it keeps working if the API is down. This also builds a player count
  history over time.
- The prebuilt Steam dataset is the main source. APIs are only called where
  the dataset is missing something.

## Analysis Standards
- Findings are described as associations, not causes, unless the data
  supports a causal claim.
- Known confounders are named for each question (for example, exclusives are
  often first-party titles with larger budgets).
- Medians are used over averages where the data is skewed.
- Sample sizes are shown on every chart. Games below a minimum review count
  are excluded (threshold to be set after exploring the data).
- Estimates are labeled as estimates.

## Tools
Python (pandas), SQL (DuckDB), Jupyter, HTML/CSS/JavaScript with Chart.js,
GitHub Actions, GitHub Pages.