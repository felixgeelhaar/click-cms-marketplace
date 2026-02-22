# Contributing plugins

Thanks for contributing to the Click CMS marketplace!

## What to submit

Each plugin needs:

1. A package zip in `packages/`.
2. A manifest json in `manifests/`.

## Manifest format

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.2.3",
  "description": "Plugin description",
  "author": "Acme",
  "packageUrl": "https://felixgeelhaar.github.io/click-cms-marketplace/packages/my-plugin-1.2.3.zip",
  "sha256": "<sha256 of the zip>",
  "manifestUrl": "https://felixgeelhaar.github.io/click-cms-marketplace/manifests/my-plugin.json"
}
```

## Packaging rules

- Zip the plugin folder itself (plugin.json + bootstrap.php at the root of the zip).
- The `packageUrl` filename must match the zip in `packages/`.
- Compute the checksum with:

```bash
shasum -a 256 packages/my-plugin-1.2.3.zip
```

## What happens on merge

GitHub Actions validates the manifest, signs it using a private key stored in secrets,
and regenerates `registry.json` automatically.
