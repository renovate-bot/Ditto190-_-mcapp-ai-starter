# Configuration

Access: `File → Preferences → Settings → Extensions → Prompt Registry`

## Settings

| Setting                                 | Description                                         | Default  |
| --------------------------------------- | --------------------------------------------------- | -------- |
| `promptregistry.installationScope`      | Installation scope (`user`, `workspace`, `project`) | `user`   |
| `promptregistry.enableLogging`          | Enable debug logging                                | `true`   |
| `promptregistry.autoCheckUpdates`       | Auto-check updates on activation                    | `true`   |
| `promptregistry.updateCheck.enabled`    | Enable update checks                                | `true`   |
| `promptregistry.updateCheck.frequency`  | `daily`, `weekly`, `manual`                         | `daily`  |
| `promptregistry.updateCheck.autoUpdate` | Auto-install updates                                | `false`  |
| `promptregistry.updateCheck.cacheTTL`   | Cache TTL (ms)                                      | `300000` |

## Export/Import Settings

- **Export**: Registry Explorer toolbar → Export button
- **Import**: Registry Explorer toolbar → Import button (merge or replace)

## Installation Paths

| Platform | Path                                              |
| -------- | ------------------------------------------------- |
| macOS    | `~/Library/Application Support/Code/User/prompts` |
| Linux    | `~/.config/Code/User/prompts`                     |
| Windows  | `%APPDATA%/Code/User/prompts`                     |

## See Also

- [Settings Reference](../reference/settings.md) — Complete settings list
- [Troubleshooting](./troubleshooting.md) — Common issues
