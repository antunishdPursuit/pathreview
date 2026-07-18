## Week 7 - Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/72

**Issue title:** Add a bias audit report that runs over a sample of stored reviews

**Tier:** [ ] Tier 1  [ ] Tier 2  [x] Tier 3

**Problem summary:**
PathReview has a bias detector, but there is not yet an offline audit report that checks how that detector performs across a sample of stored reviews. This means the project has limited visibility into where the detector may create false positives or false negatives, especially when review text includes demographic signals. A successful fix would add a script that samples stored reviews, runs them through the bias detector with clear logging, and produces a report summarizing the results. The work should mainly affect `scripts/audit_bias.py` and `safety/bias_detector.py`.

**Branch name:** feat/72-bias-audit-report

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger
