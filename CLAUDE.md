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

## Architecture

- **Root (`/`)**: Pre-built static files served by GitHub Pages. Key files: `index.html` (main page with all sections), `styles.css` (custom overrides over Hugo Academic defaults), `js/` (bundled JS), `img/` (photos and icons), `files/` (CV PDF).
