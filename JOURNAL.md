## Week 7 - Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/72

**Issue title:** Add a bias audit report that runs over a sample of stored reviews

**Tier:** [ ] Tier 1  [ ] Tier 2  [x] Tier 3

**Problem summary:**
PathReview has a bias detector, but there is not yet an offline audit report that checks how that detector performs across a sample of stored reviews. This means the project has limited visibility into where the detector may create false positives or false negatives, especially when review text includes demographic signals. A successful fix would add a script that samples stored reviews, runs them through the bias detector with clear logging, and produces a report summarizing the results. The work should mainly affect `scripts/audit_bias.py` and `safety/bias_detector.py`.

**Branch name:** feat/72-bias-audit-report

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Week 8 - Reproduction & solution planning

**Reproduction commit link:** https://github.com/antunishdPursuit/pathreview/commit/fc3d948dca0a39e1a8e9d5c88395f226fa9165bc

**Reproduction summary:**
I reproduced issue #72 as a missing-feature gap. The expected offline audit script, `scripts/audit_bias.py`, does not exist, while the reusable bias detection logic exists in `safety/bias_detector.py` through `BiasDetector.detect_bias(text)`.

**PLAN.md link:** https://github.com/antunishdPursuit/pathreview/blob/feat/72-bias-audit-report/PLAN.md

**Walkthrough video (recommended):** https://www.loom.com/share/a48973d934254ea8b9481bd80d1d820e

**Blockers or open questions:**
I still need to confirm which stored review source should be sampled and how the report should label false positives and false negatives when there is no existing ground-truth dataset.

## Week 9 - Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:** I implemented the offline bias audit for Issue #72. The script samples up to 100 completed stored reviews, combines each review's content and suggestions, runs the existing bias detector, logs each result, and generates an editable JSON report. The same script can be edited by a human to add human labels and then calculate false-positive and false-negative rates by demographic signal. I also added three unit tests that passed.

**Next steps:** Run the remaining repository checks, document unrelated existing failures, push the branch, open a draft pull request against the upstream repo, and complete Check-in 2 with the final PR information.

**Blockers:** The local database contains only five eligible completed reviews, so the audit cannot demonstrate a full 100-review sample. The full unit suite currently reports 53 failures in unrelated test files, while all three tests for the audit workflow pass.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/ascherj/pathreview/pull/763

**Branch:** `feat/72-bias-audit-report`

**What you built:** I built an offline bias audit that samples completed stored reviews, runs their combined content and suggestions through the existing bias detector, and generates an editable JSON report. After human labels are added, the same script can calculate false-positive and false-negative rates by demographic signal and generate an evaluated report.

**Tests added or updated:** I added `tests/unit/test_audit_bias.py` with three tests covering review-text extraction, labeled report evaluation and temporary-file cleanup, and invalid demographic signal rejection. All three audit tests pass. The full unit suite reported 378 passed and 53 failures in unrelated test files.

**Self-review confirmation:**
[x] `make check` introduces no new failures in the changed files. Focused Ruff, Black, and mypy checks pass. The repository-wide lint step stops on 182 unrelated existing errors.
[x] `make test-unit` introduces no new audit failures. All three audit tests pass, while the repository-wide suite has 53 failures in unrelated test files.

**Draft PR feedback received from:** none

