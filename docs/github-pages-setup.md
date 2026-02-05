---
layout: default
title: GitHub Pages Setup
---

# GitHub Pages Documentation Setup

The documentation for Azure Architecture Categoriser has been migrated to GitHub Pages. This document explains the new structure and how to manage it.

## Overview

The documentation is now hosted as a static site using:
- **GitHub Pages** for hosting
- **Jekyll** for static site generation
- **Minimal theme** for consistent styling
- **Automated deployment** via GitHub Actions

## Current Setup

### Source Location
- **Documentation source:** `/docs` folder in the repository
- **GitHub Pages configuration:** `.github/workflows/pages.yml`
- **Jekyll configuration:** `docs/_config.yml`

### Automatic Deployment

When you push changes to the `docs/` folder on the `main` branch:

1. GitHub Actions automatically triggers the `pages.yml` workflow
2. Jekyll builds the site from the `docs` folder
3. The built site is deployed to GitHub Pages
4. Your site is live at: `https://adamswbrown.github.io/azure-architecture-categoriser`

> **Note:** It may take 1-2 minutes for changes to appear online after pushing.

## File Structure

```
docs/
├── _config.yml              # Jekyll configuration
├── _layouts/
│   └── default.html         # Main page layout
├── index.md                 # Homepage
├── getting-started.md       # Getting started guide
├── recommendations-app.md
├── catalog-builder.md
├── architecture-scorer.md
├── configuration.md
├── azure-deployment.md
├── architecture-categorization-guide.md
├── drmigrate-integration.md
├── reviewing-the-catalog.md
├── securityaudit.md
├── design/
│   ├── README.md
│   ├── glossary.md
│   ├── architecture-scorer-prompt-v1.md
│   ├── catalog-builder-prompt-v1.md
│   ├── recommendations-app-prompt-v1.md
│   └── decisions/
│       ├── 0001-scoring-weights.md
│       ├── 0002-confidence-penalties.md
│       └── ...
└── images/
    └── [diagram images]
```

## Front Matter

All markdown documentation files now include Jekyll front matter at the top:

```yaml
---
layout: default
title: Page Title
---

# Page Title

...rest of content...
```

The `layout: default` uses the custom layout defined in `_layouts/default.html`, which provides:
- Navigation menu linking to all major documentation
- Consistent styling across pages
- GitHub repository links
- Footer with attribution

## Adding New Pages

To add a new documentation page:

1. **Create a new markdown file** in the `docs/` folder:
   ```bash
   touch docs/new-page.md
   ```

2. **Add Jekyll front matter** at the top:
   ```yaml
   ---
   layout: default
   title: Your Page Title
   ---
   ```

3. **Write your content** in markdown below the front matter

4. **Update navigation** (optional):
   - Edit `docs/_layouts/default.html` to add links to your new page
   - Or update `docs/_config.yml` nav_links section

5. **Push to main branch**:
   ```bash
   git add docs/new-page.md
   git commit -m "Add new documentation page"
   git push origin main
   ```

Your new page will automatically:
- Be processed by Jekyll
- Rendered with the default theme
- Available at `docs/new-page/` in the GitHub Pages site
- Indexed by search engines

## Updating Existing Pages

Simply edit any `.md` file in the `docs/` folder:

```bash
git add docs/recommendations-app.md
git commit -m "Update recommendations app docs"
git push origin main
```

Changes will be automatically deployed within 1-2 minutes.

## Links in Documentation

Use relative links for internal documentation:

```markdown
# Bad - uses full paths
[Configuration Guide](/azure-architecture-categoriser/configuration.md)

# Good - uses relative paths
[Configuration Guide](./configuration.md)
[Design](./design/)
[Scoring Weights](./design/decisions/0001-scoring-weights.md)
```

## Images

Place images in the `docs/images/` folder and reference them:

```markdown
![Alt text](./images/my-image.png)
```

## Styling

The site uses the [Minimal Jekyll theme](https://github.com/pages-themes/minimal). The theme is automatically applied by GitHub Pages.

To customize styling, you can:

1. **Create `docs/_includes/head-custom.html`** for custom CSS
2. **Create `docs/assets/css/style.scss`** to override theme styles
3. **Modify `docs/_config.yml`** for theme configuration

## Local Testing

To test your documentation locally before pushing:

### Using Jekyll locally:

```bash
# Install Jekyll (one time)
gem install jekyll bundler

# In the docs folder
cd docs
bundle install

# Start local server
bundle exec jekyll serve

# Visit http://localhost:4000
```

### Using Docker:

```bash
docker run -it --rm -v "$PWD/docs:/srv/jekyll" -p 4000:4000 jekyll/jekyll:latest jekyll serve
```

## Build Status

- **GitHub Pages build status** can be viewed in the repository Settings > Pages section
- **Workflow logs** can be viewed in Actions > pages.yml workflow
- **Deployment history** shows at the bottom of Settings > Pages

## Configuration Details

### `_config.yml` Settings

| Setting | Purpose |
|---------|---------|
| `title` | Site title in header and browser tab |
| `description` | Subtitle shown below title |
| `theme` | Uses jekyll-theme-minimal |
| `plugins` | SEO tag, sitemap generation |
| `exclude` | Files/folders not processed by Jekyll |

### GitHub Actions Workflow

The `pages.yml` workflow:

1. **Triggers on:** Push to main branch (docs folder changes)
2. **Checks out** the repository
3. **Builds** the site using Jekyll
4. **Deploys** to GitHub Pages
5. **Updates** site URL in the job summary

Runs typically complete in 30-60 seconds.

## Troubleshooting

### Site not updating
- Check the Actions workflow ran successfully
- Clear your browser cache (Cmd+Shift+R on Mac)
- Wait 1-2 minutes for GitHub to serve the updated site

### Build failed error
- Check the Actions workflow logs for the specific error
- Common issues:
  - Invalid YAML in front matter (check quotes)
  - Broken image paths
  - Invalid markdown syntax

### Links broken
- Use relative paths: `[Link](./other-page.md)`
- Not absolute paths: `[Link](/absolute/path)`

## Updating Theme

To update to a newer theme version or change themes:

1. Edit `docs/_config.yml` `theme:` line
2. Available themes:
   - `jekyll-theme-minimal` (current)
   - `jekyll-theme-architect`
   - `jekyll-theme-cayman`
   - `jekyll-theme-midnight`
   - See [GitHub Pages themes](https://pages.github.com/themes/)

3. Push changes - GitHub will automatically use the new theme

## Additional Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Pages Themes](https://pages.github.com/themes/)
- [Markdown Guide](https://www.markdownguide.org/)

