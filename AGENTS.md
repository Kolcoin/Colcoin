# AGENTS.md

## Cursor Cloud specific instructions

This is a **zero-dependency static website** (HTML + CSS + vanilla JS). There is no package manager, no build step, no framework, and no backend.

### Running the dev server

Serve files with any static HTTP server on port **4173** (referenced in sitemap, canonical URLs, and Open Graph metadata):

```
python3 -m http.server 4173 --directory /workspace
```

Then open `http://localhost:4173/`.

### Linting

- **HTML**: `npx htmlhint index.html starts/complex-98100.html`
- **JS syntax**: `node --check script.js`
- **CSS**: No suitable CLI linter is configured; csslint does not support CSS custom properties. The CSS uses modern features (`:root` variables, `clamp()`, `min()`) and is valid.

### Key files

| File | Purpose |
|---|---|
| `index.html` | Main landing page |
| `starts/complex-98100.html` | Article/detail page for project 98100 |
| `styles.css` | All styles (single file, no preprocessor) |
| `script.js` | All JS — renders cards, districts, launch blocks, and handles the lead form |
| `sitemap.xml` | Sitemap referencing `localhost:4173` |
| `robots.txt`, `llms.txt` | SEO / AI discoverability files |
| `assets/` | Gallery images for project articles |

### Notes

- The lead form (`setupLeadForm` in `script.js`) shows a `window.alert()` on submit; there is no backend.
- All project data is hardcoded in `script.js` as JS arrays/objects.
- The site expects to be served from the repository root (relative paths like `./styles.css`, `./script.js`).
