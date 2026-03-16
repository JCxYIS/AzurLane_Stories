# Azur Lane Stories

The memory archive for Azur Lane, automatically generated and hosted on GitHub Pages.

> **Live Site**: [https://jcxyis.github.io/AzurLane_Stories](https://jcxyis.github.io/AzurLane_Stories)

| ![alt text](https://static.jcxyis.com/images/QtYY801Vrj.webp) | ![alt text](https://static.jcxyis.com/images/hVJJS9hqbs.webp) |
| ------------------------------------------------------------- | ------------------------------------------------------------- |

## Automated Update

This project includes a GitHub Actions workflow that automatically checks for updates from [AzurLaneData Repository](https://github.com/AzurLaneTools/AzurLaneData), and regenerates the site daily.

## Keyboard Shortcuts

- `i`: Toggle debug info (Index Page)
- `o`: Toggle UI (Story Page)

## Development note

### Requirements

- Game data is required for generation. Run `./setup-source.sh` to prepare the necessary data to parse.

### Generation

- To generate the site, simply run

  ```bash
  python3 src/main.py
  ```

  - Use the `--overwrite` flag to force regeneration of all story JSON files.
  - The generated site files (HTML, JS, CSS, and Data) will be saved in the `output/` directory.

### Local Preview

- To view the site locally, navigate to the `output/` directory and start a web server, for instance:
  ```bash
  cd output
  python3 -m http.server 5000
  ```

### Github Actions workflow

See `.github/workflows/update-site.yml`.

- The workflow is triggered daily at 12:00 UTC (20:00 UTC+8), or when the `main` branch is updated
- Checks for updates from AzurLaneData Repository
- Regenerates the site on demand and pushes the changes to the `web` branch

## Data Sources & Credits

- **Data**: Data fetched and parsed from [AzurLaneData by AzurLaneTools](https://github.com/AzurLaneTools/AzurLaneData).
- **Assets**: Audio and images are sourced from [Azur Lane Utility (azurlane.nagami.moe)](https://azurlane.nagami.moe/) and [Azur Lane Resources by Fernando2603](https://github.com/Fernando2603/AzurLane/tree/main).
- **Inspired by** [Azur Lane Wiki/Memories](https://azurlane.koumakan.jp/wiki/Memories).

> **Disclaimer**: All game assets, images, and audio belong to their respective owners. This site is a fan-made project and is not affiliated with the official Azur Lane project.
