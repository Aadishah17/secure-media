# React Tailwind Upload UI Design

## Goal

Create a clean React + Tailwind upload interface in this empty repository. The first screen should be the usable upload experience, not a landing page.

## Architecture

Use a Vite React app with Tailwind CSS. Keep the structure small:

- `src/App.jsx` owns the upload UI state and layout.
- `src/index.css` defines Tailwind imports and lightweight global styling.
- Vite and Tailwind config files stay standard.

## UI

Build a responsive single-page upload workspace with clear spacing, restrained styling, and predictable states:

- Header area with concise product context.
- Main upload panel with file picker and drag/drop support.
- Preview area for the selected image.
- Result area showing duplicate/original status, similarity, and best match placeholders.
- Error and loading states that do not shift the layout excessively.

Use Tailwind spacing, border, shadow, and color utilities directly. Avoid nested cards, oversized hero treatment, decorative gradients, or one-note color palettes.

## Behavior

For now, handle image selection locally and show preview/result UI scaffolding. Keep API integration isolated so a Flask upload endpoint can be wired later without changing layout structure.

## Accessibility

Use semantic buttons, labels, focus states, and readable contrast. Ensure the upload controls work with keyboard interaction and that text fits on mobile widths.

## Verification

Install dependencies, run the app locally, and verify the layout renders without overlap on desktop and mobile-sized viewports.
