# Federal CIO Intelligence Command Center

**Current application release: v9.4**

An independent, open-source, public-source intelligence dashboard for federal IT leadership. It brings together cybersecurity developments, federal policy publications, technology intelligence, and evidence-linked executive review.

**Independent research project. Not an official U.S. government website, product, or service. Not affiliated with or endorsed by any federal agency.**

**[Open the Command Center](https://alanairesearchlab-dev.github.io/federal-cio-command-center/)** · [Intelligence Workspace](https://alanairesearchlab-dev.github.io/federal-cio-command-center/intelligence.html) · [About & Methodology](https://alanairesearchlab-dev.github.io/federal-cio-command-center/about.html)

## What is available

| Area | Capabilities |
| --- | --- |
| **Dashboard** (`index.html`) | Executive overview, CISA KEV and cyber news, Federal Register monitoring, vendor comparisons, source health, executive assessment cards, and copyable executive brief |
| **Intelligence Workspace** (`intelligence.html`) | Intelligence triage, policy change tracker, executive briefing, vendor intelligence, CVE correlations, and browser-local preferences |
| **About & Methodology** (`about.html`) | Sources, collection approach, interpretation guidance, and limitations |

The three pages share a consistent navigation shell. The project is a static GitHub Pages application, not an authenticated agency system.

### Executive intelligence (v9.1–v9.4)

- **v9.1, Since Your Last Review:** Compare currently collected public records with a checkpoint saved in this browser. A user must explicitly select **Mark as reviewed**; opening the page does not mark items reviewed. The initial visit establishes a baseline rather than labeling the entire existing catalog as new.
- **v9.1, Executive Action Calendar:** Show source-reported CISA KEV due dates over 7-day or 30-day horizons. Dates are not a determination of organizational applicability, exposure, or compliance.
- **v9.2, Executive Intelligence Assessment:** Generate rule-based cards describing what changed, why it matters, considerations for review, evidence confidence, and links to underlying public sources. Assemble a copyable executive brief.
- **v9.3, Federal Relevance Layer:** Separate threat significance from estimated federal enterprise relevance. Recognized enterprise technologies receive a relevance boost; consumer-oriented technologies may be surfaced in **Technology Watch** rather than dominate the executive assessment. This is heuristic categorization, **not** evidence that any agency deploys or does not deploy a product.
- **v9.4, Executive Responsibility Routing:** Suggest a functional review area, such as network security, enterprise applications, identity, acquisition and supply chain, infrastructure, or federal policy. Routing labels are suggestions, not official assignments.

**Important:** The assessment score is a **review-priority heuristic**, not a vulnerability severity score, risk calculation, legal determination, or measurement of agency exposure. Classifications use fields available in collected feeds, including titles and catalog metadata; they do not constitute a full-text review of every linked source. Verify consequential decisions against primary sources.

## Public data sources

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
data/                       Generated public-source JSON snapshots
.github/workflows/collect.yml  Scheduled collection and data commits
.github/workflows/validate.yml HTML/script validation on changes
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

The **Validate static application** GitHub Actions workflow checks Python syntax, inline JavaScript syntax (using Node.js), and the presence of navigation links across the three pages. It runs on relevant pushes and pull requests, and can be triggered manually. To run locally with Python 3.12+ and Node.js 20+:

```bash
python -m compileall -q scripts
python scripts/validate_static.py
```

These are **static checks**, not browser integration tests. They do not detect undefined JavaScript variables at runtime or guarantee correct data rendering. Live-page verification remains necessary.

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
