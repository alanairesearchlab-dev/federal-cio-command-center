# Federal CIO Intelligence Command Center

**Current application release: v9.8 (consolidation pass)**

An independent, open-source, public-source intelligence dashboard for federal IT leadership. It brings together cybersecurity developments, federal policy publications, technology intelligence, and evidence-linked executive review.

**Independent research project. Not an official U.S. government website, product, or service. Not affiliated with or endorsed by any federal agency.**

**[Open the Command Center](https://alanairesearchlab-dev.github.io/federal-cio-command-center/)** · [Executive Briefing](https://alanairesearchlab-dev.github.io/federal-cio-command-center/briefing.html) · [Intelligence Workspace](https://alanairesearchlab-dev.github.io/federal-cio-command-center/intelligence.html) · [About & Methodology](https://alanairesearchlab-dev.github.io/federal-cio-command-center/about.html)

## What is available

| Area | Capabilities |
| --- | --- |
| **Dashboard** (`index.html`) | Operational overview, CISA KEV, Federal Register monitoring, vendor comparisons, source health, and federal policy watch |\n| **Executive Briefing** (`briefing.html`) | Prioritized intelligence assessment, five-minute brief, change review, and source-reported action calendar |
| **Intelligence Workspace** (`intelligence.html`) | Technology Intelligence Hub, intelligence triage, policy change tracker, executive briefing, vendor intelligence, CVE correlations, and browser-local preferences |
| **About & Methodology** (`about.html`) | Sources, collection approach, interpretation guidance, and limitations |

The four pages share a consistent navigation shell. The project is a static GitHub Pages application, not an authenticated agency system.

### Executive intelligence (v9.1–v9.4)

- **v9.1, Since Your Last Review:** Compare currently collected public records with a checkpoint saved in this browser. A user must explicitly select **Mark as reviewed**; opening the page does not mark items reviewed. The initial visit establishes a baseline rather than labeling the entire existing catalog as new.
- **v9.1, Executive Action Calendar:** Show source-reported CISA KEV due dates over 7-day or 30-day horizons. Dates are not a determination of organizational applicability, exposure, or compliance.
- **v9.2, Executive Intelligence Assessment:** Generate rule-based cards describing what changed, why it matters, considerations for review, evidence confidence, and links to underlying public sources. Assemble a copyable executive brief.
- **v9.3, Federal Relevance Layer:** Separate threat significance from estimated federal enterprise relevance. Recognized enterprise technologies receive a relevance boost; consumer-oriented technologies may be surfaced in **Technology Watch** rather than dominate the executive assessment. This is heuristic categorization, **not** evidence that any agency deploys or does not deploy a product.
- **v9.4, Executive Responsibility Routing:** Suggest a functional review area, such as network security, enterprise applications, identity, acquisition and supply chain, infrastructure, or federal policy. Routing labels are suggestions, not official assignments.

**Important:** The assessment score is a **review-priority heuristic**, not a vulnerability severity score, risk calculation, legal determination, or measurement of agency exposure. Classifications use fields available in collected feeds, including titles and catalog metadata; they do not constitute a full-text review of every linked source. Verify consequential decisions against primary sources.

## Public data sources

NIST cybersecurity and information technology RSS updates are collected as a separate research category, not as binding directives. Newly added feeds appear after the next successful collection.

- **CISA Known Exploited Vulnerabilities (KEV):** Official catalog; the collector may use CISA's own public GitHub KEV mirror if the primary endpoint fails.
- **Federal Register:** Public documents API, using broad keyword discovery. A matching document is not necessarily applicable to federal CIOs.
- **CISA alerts/advisories:** Public feed collection is attempted; some CISA RSS endpoints may block automated access. Failures are recorded rather than silently presented as successful collection.
- **Cybersecurity reporting:** Public headlines and outbound links from BleepingComputer, Krebs on Security, and The Hacker News. These are third-party reports, not government directives.

Sources can fail, change format, or become stale. Review source-health information and the linked original documents before taking action.

## How it works

1. `.github/workflows/collect.yml` runs on a schedule (every four hours, subject to GitHub Actions delays) and on manual dispatch.
2. `scripts/collect.py` retrieves public-source material and writes JSON snapshots under `data/`.
3. `scripts/intelligence.py` derives normalized, explainable intelligence data and cross-source relationships.
4. GitHub Pages serves `index.html`, `intelligence.html`, `about.html`, and the committed JSON files.
5. Dashboard assessments and review tracking are generated client-side from the available snapshots. Review checkpoints and preferences stay in browser storage, not in a hosted user account.

No paid AI API, authentication, private agency records, or internal government connection is required. The dashboard does not scan endpoints or establish which products any organization uses.

## Repository layout

```text
index.html                  Executive dashboard
intelligence.html           Intelligence Workspace
about.html                  Methodology and limitations
scripts/collect.py          Public-source collectors
scripts/intelligence.py     Normalized intelligence generation
scripts/validate_static.py Static HTML and inline JavaScript syntax checks
scripts/smoke.cjs         Chromium browser runtime smoke tests
data/                       Generated public-source JSON snapshots
.github/workflows/collect.yml  Scheduled collection and data commits
.github/workflows/validate.yml HTML/script and Chromium browser tests on changes
README.md                   Project documentation
```

## Run locally

From the repository root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/`. The application uses relative paths to its JSON data. Local preview does not require additional Python packages.

To refresh the data locally, run:

```bash
python scripts/collect.py
python scripts/intelligence.py
```

These collection scripts make outbound public network requests.

## Build validation

The **Validate static application** GitHub Actions workflow runs Python compilation, inline JavaScript syntax checks, navigation checks, and a **real Chromium browser smoke test** on relevant pushes and pull requests. Browser tests load all three pages, verify navigation, exercise dashboard assessment and brief rendering, load the intelligence workspace, and fail on uncaught browser errors.

To run the static checks locally with Python 3.12+ and Node.js 20+:

```bash
python -m compileall -q scripts
python scripts/validate_static.py
```

To run the browser smoke test locally, install Playwright and Chromium, then run `node scripts/smoke.cjs`. The test starts its own local HTTP server. Passing smoke tests are not a substitute for source accuracy review, accessibility testing, or complete end-to-end testing.

The collector retries transient HTTP 429/5xx and network failures, with bounded response sizes. HTTP 403 access denials are **not** bypassed or silently reported as successful; the last successful feed snapshot is retained when available.

## Deploy with GitHub Pages

1. Fork or clone this public repository.
2. In **Settings → Pages**, publish the `main` branch from the repository root.
3. Enable GitHub Actions with permission to commit generated data, if using the included collector.
4. Manually run **Collect public intelligence** once to populate snapshots.
5. Open the published GitHub Pages URL.

GitHub Pages deployments and scheduled Actions may be delayed. Static assets and browser caches can also delay the appearance of a newly committed release.

## Release history

| Release | Main change |
| --- | --- |
| **v9.4** | Executive responsibility routing and rationale |
| **v9.3** | Federal enterprise relevance and Technology Watch distinction |
| **v9.2** | Executive assessments, transparent scoring, copyable briefing |
| **v9.1** | Since Your Last Review and CISA KEV action calendar |
| **v9.0** | Unified three-page navigation and consistent application shell |
| **v8.2** | Vendor intelligence usability, tailored briefings, CISA mirror fallback |
| **v8.1** | Explainable triage, policy filtering, vendor watchlists |
| **v8.0** | Intelligence Workspace and normalized intelligence data |
| **v7** | Security news and advisory feeds |

## Accuracy, security, and independence

This is **public information for independent research**. It is not a government system or a compliance service. The software does not know an organization's asset inventory, patch state, exposure, authorizing decisions, contracts, or applicable legal obligations.

- A KEV listing signals known exploitation, not confirmed exposure in any specific environment.
- A CISA catalog due date must be interpreted with the applicable directive and current guidance.
- A Federal Register publication date is not automatically an effective date or compliance deadline.
- Automated attention, relevance, and routing labels can be wrong or incomplete.
- Browser-local settings may be lost when storage is cleared and are not synchronized across devices.
- Source feeds may be delayed or unavailable; retain appropriate skepticism about freshness.
- Do not add credentials, private records, confidential data, or nonpublic agency information to this repository.

Contributions and issue reports should use public, non-sensitive examples only.

See [About & Methodology](about.html) for further interpretation guidance.

## Browser visual quality checks

Every HTML/script change triggers Chromium checks at desktop (1440 × 900) and mobile (390 × 844) widths. The workflow captures full-page screenshots of all four pages, verifies navigation, checks horizontal overflow, and exercises key application behavior. Screenshots are uploaded as a downloadable **browser-screenshots** artifact in the [Validate static application workflow](https://github.com/alanairesearchlab-dev/federal-cio-command-center/actions/workflows/validate.yml), including on test failure when images are available. Artifacts are retained for 14 days.

These screenshots provide a review trail, **not yet automated pixel-difference regression detection**. Dynamic feed content and timestamps make unmasked pixel baselines noisy; a future approved, stable baseline can add targeted screenshot comparisons. The tests run against the checked-out GitHub Pages site locally, not against the currently deployed production URL.

## v9.6: Decision support and quality controls

- **Policy lifecycle signals:** Combine the collected Executive Order and OMB indexes into a policy watch. Title terms such as amend, revoke, rescind, and supersede are **review cues only**, not confirmed legal relationships or status determinations. Missing sources remain explicitly unavailable.
- **Cross-source intelligence correlation:** Group public security reports by exact CVE identifier when the same CVE appears in CISA KEV. Reports are grouped, not counted as additional vulnerabilities.
- **Collection diagnostics:** Display per-source check time, last successful retrieval, and errors. A failed source is not treated as a clean result.
- **Executive export:** Executive Briefing includes a Print / Save as PDF control with a print stylesheet. PDF generation uses the browser's print dialog.
- **Structural visual regression:** Chromium checks shared navigation geometry across all four desktop pages, alongside mobile overflow checks and eight desktop/mobile screenshots. Pixel-difference baseline comparisons are not yet implemented.

Policy and CVE enrichment is generated after the four-hour public collector runs. The first successful run establishes the initial derived snapshots. This project never assumes an organization's asset inventory, obligations, or exposure.

## v9.7: Technology Intelligence Hub

The Intelligence Workspace now has a dedicated Technology Intelligence section without adding another top-level page. A bounded collector checks **40 candidate public RSS/Atom publishers** every four hours. Actual successful endpoints are reported separately from candidates; blocked or missing feeds are never bypassed. Newsroom view defaults to **12 ranked story clusters**, offers six topic filters, search, progressive disclosure, and a publisher directory showing source failures and last successful retrieval. Automated clustering uses title similarity, so unrelated or distinct events may be grouped incorrectly; original publisher links are retained.

## Repository hygiene and privacy

- `.gitignore` excludes local dependencies, screenshots, temporary files, and common credential file types.
- `scripts/privacy_scan.py` runs in CI against tracked files and flags explicit agency identifiers, selected staff names, private key markers and credential-shaped literals. It is a **guardrail, not a complete secret scanner or historical Git audit**.
- The project intentionally contains no staff acknowledgments, organizational affiliation, private operational details, or internal incident information. GitHub account identity, commit author metadata, and any email addresses already associated with the GitHub account remain visible under GitHub's normal behavior.
- Public feeds and quoted publisher names are external sources, not contributors or endorsements.

## v9.8 consolidation pass

- Added decision-oriented quick links in Intelligence Workspace and direct-linkable section URLs (`#technology`, `#policy`, `#triage`, `#vendor`).
- Renamed the detailed workspace export to **Research Brief Builder** to distinguish it from the authoritative executive-facing **Executive Briefing** page.
- Expanded browser checks to verify that direct links select the expected section.
- Preserved existing functionality and the four-page navigation. Further data retention and source-quality review remain separate maintenance work; this pass does not claim a complete refactor or history scrub.

### Dashboard decision-first sweep

The Dashboard now opens with four concise decision shortcuts: leadership priorities, security investigation, federal policy, and technology changes. These link directly to the relevant workspace section without duplicating its content. The redundant executive-briefing shortcut panel was removed. Chromium checks enforce the shortcut links and absence of that duplicate panel.
