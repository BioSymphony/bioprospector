# Release Checks

From the full source checkout, use Python 3.11+, Git, and Make. Install the
development extras and run the release check.

```bash
python3 -m pip install -e '.[dev]'
make release-check
```

The check runs tests, builds and installs a wheel, validates documentation
and example campaigns, generates demo outputs, and audits the checkout and
runtime artifacts.

If Gitleaks is available, scan Git history and the working tree.

```bash
gitleaks git --no-banner --redact=100 .
gitleaks dir --no-banner --redact=100 .
```

See the [release checklist](PUBLIC_SWITCH_CHECKLIST.md) for content review.
