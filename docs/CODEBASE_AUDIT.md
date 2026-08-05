# VNL Predictor Codebase Audit

Audit date: August 5, 2026

## Verified working

- React routes: Home, Visualization, Lookup, and Prediction
- Direct loading of client routes through the Vercel rewrite
- CSV loading, parsing, and shared in-browser caching
- Visualization filters, scatter chart rendering, and player counts
- Player search, selection, and stat-group navigation
- Match prediction from the UI through the Python API
- Winner probability and set-score responses
- Player CSV merge, all seven rating calculations, and rating merge
- Winner and set-score model training
- Synchronization of generated data/model deployment copies
- Desktop and 390px-wide mobile navigation/layout
- Current Volleyball World selectors for player statistics, schedule cards,
  and advanced standings

## Important limitations

### The data is a 2025 snapshot

The checked-in match and team data is from the 2025 men's VNL season. The
player-stat URLs do not include a season identifier and currently resolve to
Volleyball World's active competition. A future scrape must update player,
team, and match sources as one season-consistent batch.

### Model evaluation is not yet a production-quality forecast estimate

The model uses final season standings to predict matches from that same season.
That leaks future season information into historical match features. Grouped
cross-validation is useful for regression testing the pipeline, but its score
should not be presented as a true prospective accuracy estimate. A trustworthy
evaluation requires pre-match rolling standings or multiple historical seasons.

### External scraping can still change

Live selector smoke tests pass, but Volleyball World can change markup or
anti-automation behavior without notice. Full scrapes intentionally were not run
during this audit because they overwrite checked-in datasets.

### Dependency audit context

The client stays on React 18 and React Router 6 to avoid an unnecessary
application-framework migration. The current npm advisory report contains two
moderate React Router advisories involving redirects/SSR deserialization. This
app supplies only fixed internal routes, performs no SSR hydration, and never
passes user input to a redirect target. Moving router and React major versions
should be handled as a separate migration with the same browser regression suite.

## Optimization results

- Initial production JavaScript: 432 KB → approximately 167 KB
- Chart.js loads only on the Visualization route
- The CSV is fetched and parsed once per browser session, then shared by pages
- Filter membership checks use sets/maps instead of repeated array scans
- API data is indexed once and models are cached once per warm server instance
- Warm local prediction calls complete in roughly 5 ms
- Team aliases now resolve consistently across player and standings datasets
- Training features now include player impact for all 116 matches
- Standardized logistic models converge without the previous solver warning
- Grouped mean CV accuracy: 54.1% → 57.6% on the same dataset
- Rating calculation is vectorized and reproduces all previous ratings exactly
- Two accidental duplicate player rows were removed
- Scraper imports no longer open Chrome or begin network work
- Generated artifacts have an explicit sync/check command

## Verification commands

```sh
python -m unittest discover -s tests -v
python -m compileall -q Collection ML RatingSystem scripts vnl-visualizer/api
python scripts/sync_artifacts.py --check

cd vnl-visualizer
npm ci
npm run check
```
