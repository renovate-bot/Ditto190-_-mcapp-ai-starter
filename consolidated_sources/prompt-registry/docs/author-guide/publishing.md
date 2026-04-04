# Publishing Collections

## GitHub (Recommended)

### Setup

1. Scaffold a new repository: `Ctrl+Shift+P` → "Prompt Registry: Scaffold Project" → `Awesome Copilot Project`
2. Choose an empty folder where the repository should be bootstrap
3. Update the content of different folder and collections files
4. Validate your collection [Validation](./validation.md)
5. Create a new repository in your github organization
6. Do the initial commit and push to your new repository

### Update the content of your collection

```yaml
id: my-collection
name: My Collection
version: 1.0.0
description: What this collection does
```

### Users Install Via

```bash
Ctrl+Shift+P → "Add Source" → Collection from Github repository → Name of the source → Link to your repository you just published → remaining can remain as default
```

- Once source is added refresh your marketplace and search for your bundles you can install them

## Updating

1. Push a new commit in your repo
2. Users will need to sync

Users update via: Right-click bundle → "Check for Updates"

## See Also

- [Creating Collections](./creating-source-bundle.md)
- [Collection Schema](./collection-schema.md)
- [Validation](./validation.md)
