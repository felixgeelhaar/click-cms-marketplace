# Click CMS Marketplace Registry

This repository hosts the public `registry.json` and plugin manifests for Click CMS.

`registry.json` is served via GitHub Pages.

## Automation

On merge to `main`, GitHub Actions signs all manifests and rebuilds `registry.json`.
The private key is stored in the `MARKETPLACE_PRIVATE_KEY` secret.
