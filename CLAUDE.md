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

### Group member photos

Circular thumbnails are displayed at **80×80 px** using `object-fit: cover; border-radius: 50%` on a square `<img>`. Because the source image is square and object-fit does not crop it further, the entire square is scaled into the circle. This means **the face must be centered in the square output image** — off-center faces will appear off-center in the circle.

**Workflow for adding or updating a photo:**

1. Save the original source to `files/group_originals/<name>_original.<ext>` as a backup.
2. Crop and resize to **400×400 px** using ImageMagick:
   ```bash
   magick <source> -crop WxH+X+Y +repage -resize 400x400 img/group/<name>.jpg
   ```
3. Visually verify the result: the face should be **centered** and **not too tightly cropped** — aim to include the full head with some breathing room above and below (roughly shoulders visible at the bottom, a small margin above the hair at the top).
4. Update `index.html` to reference the new image and add `data-original="files/group_originals/<name>_original.<ext>"` for the hover popup.

**Centering math:** To center a face horizontally, set `X = face_center_x - crop_width/2`. Increasing `X` or `Y` shifts the crop window right/down in the original, which shifts the face left/up in the output.

**Tightness guidance:** Crops should be loose enough that the face is not filling the entire circle edge-to-edge. Compare against existing members (Jason, Jack) for a consistent feel. If a crop looks like a passport photo, it is probably too tight.

## Site colors

| Role | Value |
|---|---|
| Primary / navbar background | `#13294B` (UIUC Navy) |
| Accent / hover / underlines | `#FF5F05` (UIUC Orange) |
| Active filter button underline | `box-shadow: inset 0 -3px 0 #FF5F05` on navy background |

These two colors are the University of Illinois official brand colors and should be used consistently for any new UI elements.

## Architecture

- **Root (`/`)**: Pre-built static files served by GitHub Pages. Key files: `index.html` (main page with all sections), `styles.css` (custom overrides over Hugo Academic defaults), `js/` (bundled JS), `img/` (photos and icons), `files/` (CV PDF).
- **`img/group/`**: 400×400 square JPGs for group member circular thumbnails.
- **`files/group_originals/`**: Original (unmodified) source photos for all group members and the biography portrait, used as hover popup previews and crop source.
