# Tests

The small test suite exercises deterministic Atlas interfaces offline. Synthetic data never represents datalens production knowledge.

- `test_frontmatter.py`, `test_ids.py`, and `test_links.py` cover the small parsing and identity helpers.
- `test_lint.py` covers frontmatter semantics, structured target validation and relative Markdown file links. It also confirms that body headings, prose, remote URLs, review age and secret judgment are outside deterministic lint.
- `test_maps.py` uses one coherent fictional system to cover sparse map compilation, reverse routes, page-attributed structured errors, deterministic bytes and freshness detection.

Run `pytest`.
