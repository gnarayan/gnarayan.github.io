# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the GitHub Pages repository for Gautham Narayan's personal academic website (`gnarayan.github.io`). The **root directory contains pre-built static HTML output** of a Hugo Academic 3.1.1 site (Hugo 0.57.2). The Hugo source files for the main site are not stored here — only the compiled output is committed for deployment.

## Deployment

Pushing to `master` deploys directly to GitHub Pages at `https://gnarayan.github.io/`. There is no build step for the main site — edits to the HTML at the root are deployed as-is.

## Common Tasks

### Updating the CV
Replace the PDF file at `files/GauthamNarayan_CV.pdf`. The filename must stay the same as it's referenced from the pre-built HTML.

### Editing site content
Since the Hugo source for the main site is not in this repo, content changes require editing the compiled HTML files directly. The main page content is in `index.html`. Publication listings are in `publication/`, posts in `post/`, etc.

**Important:** `index.html` is large and complex. The Edit tool can fail on multi-line replacements. When an edit fails or the match is ambiguous, use a Python replace script instead:
```bash
python3 - <<'EOF'
with open('index.html', 'r') as f:
    content = f.read()
content = content.replace(
    'exact old string',
    'exact new string'
)
with open('index.html', 'w') as f:
    f.write(content)
EOF
```

### Updating the copyright year

Both `index.html` and `404.html` contain the copyright year and must be updated together. Search for `&copy; Gautham Narayan` in both files.

### Adding a recorded talk

Talks are displayed as a 3-column thumbnail gallery in the "Recorded Talks" section of `index.html`. Each card uses a YouTube thumbnail as the preview image. To add a new talk:

1. Get the YouTube video ID from the URL (e.g. `dQw4w9WgXcQ` from `youtube.com/watch?v=dQw4w9WgXcQ`).
2. The thumbnail URL is: `https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg`
3. Copy an existing `.talk-card` block in `index.html` and update the `data-videoid`, `data-title`, thumbnail `src`, and `alt` attributes.

### Adding a group member

Each group member card in `index.html` uses several `data-*` attributes that drive the hover popup and click behavior:

- `data-original="files/group_originals/<name>_original.<ext>"` — full-size photo shown on hover (required)
- `data-name="Full Name"` — name shown in hover popup (required)
- `data-url="/path/or/url"` — if present, clicking the photo opens this URL

Copy an existing card block and update the name, role, photo path, and these attributes. Then follow the group photo workflow above to prepare the image.

### Linking personal webpages for group members and alumni

Group member cards support a `data-url` attribute that makes the photo clickable (opens the URL in a new tab). Alumni entries are plain HTML list items. When adding or updating a personal webpage link:

**Current group members** (in the Group section card):
1. Add/update `data-url="https://..."` on the `<img class="group-photo">` element (enables click-on-photo).
2. Wrap the member's name text in `<a href="https://..." target="_blank" rel="noopener">Name</a>`.

**Alumni** (in the Alumni section list):
- Wrap the name in `<a href="https://..." target="_blank" rel="noopener">Name</a>` pointing to their primary personal or professional page (personal site preferred over institutional directory).
- For alumni with both a personal/employer page and an institutional degree page, use a dual-link pattern: name → primary page, degree institution text → institutional page. Example:
  ```html
  <a href="https://pnnl.gov/people/andrew-engel">Andrew Engel</a> … Ph.D., <a href="https://physics.osu.edu/people/engel.250">Ohio State</a>
  ```

When asked to find personal webpages, search for each person's name + institution/field. Present the list of found URLs for user review **before** making any edits to `index.html`. The user has a strong preference for accuracy — do not link pages you are not confident about. If the user supplies a URL directly, use it without question.

### Keeping the website consistent with the CV

Periodically read `files/GauthamNarayan_CV.pdf` and compare its content (positions, grants, publications, students, teaching) against the corresponding sections in `index.html`. When discrepancies are found, **do not edit `index.html` directly** — present a list of proposed changes to the user for review and approval before making any edits.

### Group member photos

Circular thumbnails are displayed at **110×110 px** using `object-fit: cover; border-radius: 50%` on a square `<img>`. Because the source image is square and object-fit does not crop it further, the entire square is scaled into the circle. This means **the face must be centered in the square output image** — off-center faces will appear off-center in the circle.

**Workflow for adding or updating a photo:**

1. Save the original source to `files/group_originals/<name>_original.<ext>` as a backup.
2. Crop and resize to **400×400 px** using ImageMagick:
   ```bash
   magick <source> -crop WxH+X+Y +repage -resize 400x400 img/group/<name>.jpg
   ```
3. Visually verify the result: the face should be **centered** and **not too tightly cropped** — aim to include the full head with some breathing room above and below (roughly shoulders visible at the bottom, a small margin above the hair at the top).
4. Update `index.html` to reference the new image and add `data-original="files/group_originals/<name>_original.<ext>"` for the hover popup.

**Centering math:** To center a face horizontally, set `X = face_center_x - crop_width/2`. Increasing `X` or `Y` shifts the crop window right/down in the original, which shifts the face left/up in the output. This is counterintuitive — shifting the crop window right moves the face *left* in the output, and vice versa.

**Tightness guidance:** Crops should be loose enough that the face is not filling the entire circle edge-to-edge. Compare against existing members (Jason, Jack) for a consistent feel. If a crop looks like a passport photo, it is probably too tight.

### Biography portrait

The biography portrait is `img/Narayan.jpg`, displayed at **320×320 px** (currently stored at 400×400). It uses the same `border-radius: 50%` circular display as group photos, so the same centering rules apply. The hover popup uses `files/group_originals/gautham_original.jpeg` as the full-size preview.

**Updating the portrait:**

1. Copy the new source to `files/group_originals/gautham_original.jpeg` (overwrite).
2. Crop and resize to **400×400 px**:
   ```bash
   magick files/group_originals/gautham_original.jpeg -crop WxH+X+Y +repage -resize 400x400 img/Narayan.jpg
   ```
3. If the new source is a less-cropped or Lightroom-processed version of a previously used photo, **recover the last good version from git** as a visual reference before iterating:
   ```bash
   git show HEAD~N:img/Narayan.jpg > /tmp/narayan_old.jpg
   ```
   Use shared background landmarks (slide text, logos, room features) to align the new crop to the same composition.
4. Centering target: eyes (not ears) should be horizontally centered. The face should sit in the upper-center of the square with shoulders visible at the bottom.

### Funding and projects logo bar

The logo bar sits between the bottom hero image and the contact section in `index.html`. It is a full-width `<div class="footer-logos">` (outside any Bootstrap container), bracketed above and below by `<hr class="section-divider">` (1px solid #222, margin 0).

**Structure:** Two groups inside `.footer-logos-groups` — "Funding Agencies" on the left (NSF, DOE, Simons, LSST DA, NASA) and "Projects & Surveys" on the right (SkAI, DESC, SCiMMA, YSE), separated by a `.footer-logos-divider` vertical line.

**Adding a logo:**
1. Save the image to `img/logos/logo-<name>.png` (or `.svg`). SVGs work well for scalable logos.
2. Add an `<a class="footer-logo-link">` + `<img class="footer-logo">` block inside the appropriate `.footer-logos-row`.
3. Default logo height is **45px**. For wide text-heavy logos that would dominate the row, add a specific override class (e.g. `.footer-logo-skai { height: 35px; }`) to keep horizontal footprints comparable.
4. The bar uses `flex-wrap: nowrap` — **verify logos still fit on one line** at the MacBook Air viewport (~1280px) after adding anything. If they don't, reduce gaps or add a height override.

**Recoloring a transparent-background logo** (e.g. to match site palette):
```bash
magick input.png \( +clone -alpha extract \) \( -clone 0 -fill '#00B68C' -colorize 100 \) -delete 0 +swap -alpha off -compose CopyOpacity -composite output.png
```
The SCiMMA logo was recolored to `#00B68C` (Rubin Observatory green) this way.

**SCIMMA and YSE** have inline text labels to the right of their logos (`.footer-logo-labeled` wrapper):
- SCiMMA: "scimma.org" in Montserrat, `#00B68C`, 0.78rem
- YSE: "Young / Supernova / Experiment" stacked, 0.55rem, height fixed to match logo (35px)

## Site colors

| Role | Value |
|---|---|
| Primary / navbar background | `#13294B` (UIUC Navy) |
| Accent / hover / underlines | `#FF5F05` (UIUC Orange) |
| Active filter button underline | `box-shadow: inset 0 -3px 0 #FF5F05` on navy background |

These two colors are the University of Illinois official brand colors and should be used consistently for any new UI elements.

**Do not use CSS custom properties (`var()`) for these colors in `styles.css`.** When `var()` fails to resolve (e.g. due to parse order or caching), the CSS fallback for `background` is `transparent`, which makes the navbar background invisible while its hardcoded `color: #fff` nav text remains white — white text on a white page. Use the hardcoded hex values directly.

## Architecture

- **Root (`/`)**: Pre-built static files served by GitHub Pages. Key files: `index.html` (main page with all sections), `styles.css` (custom overrides over Hugo Academic defaults), `js/` (bundled JS), `img/` (photos and icons), `files/` (CV PDF).
- **`img/group/`**: 400×400 square JPGs for group member circular thumbnails.
- **`img/logos/`**: Funding agency and project/survey logos for the footer bar. PNG or SVG. Rubin green `#00B68C` used for SCiMMA logo.
- **`files/group_originals/`**: Original (unmodified) source photos for all group members and the biography portrait, used as hover popup previews and crop source.
