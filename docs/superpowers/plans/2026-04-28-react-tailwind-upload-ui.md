# React Tailwind Upload UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clean Vite React + Tailwind upload UI in the empty repository.

**Architecture:** Create a small single-page app. `src/App.jsx` owns upload state, preview behavior, and the visible workspace; `src/index.css` owns Tailwind import and base styling; config files stay standard.

**Tech Stack:** Vite, React, Tailwind CSS, Vitest, Testing Library.

---

## File Structure

- Create `package.json` for scripts and dependencies.
- Create `index.html` as the Vite entry document.
- Create `vite.config.js` with React, Tailwind, and Vitest jsdom configuration.
- Create `src/main.jsx` to mount React.
- Create `src/App.jsx` for the upload interface and helpers.
- Create `src/App.test.jsx` for upload behavior tests.
- Create `src/index.css` for Tailwind and global base styles.
- Create `.gitignore` for generated dependencies and build output.

### Task 1: Project Scaffold

**Files:**
- Create: `package.json`
- Create: `index.html`
- Create: `vite.config.js`
- Create: `src/main.jsx`
- Create: `src/index.css`
- Create: `.gitignore`

- [ ] **Step 1: Create the app scaffold**

Write the standard Vite React files with Tailwind wired through `@tailwindcss/vite`, npm scripts for `dev`, `build`, `preview`, and `test`, and a root element in `index.html`.

- [ ] **Step 2: Install dependencies**

Run: `npm install`
Expected: dependencies install and `package-lock.json` is created.

- [ ] **Step 3: Commit scaffold**

Run:

```bash
git add package.json package-lock.json index.html vite.config.js src/main.jsx src/index.css .gitignore
git commit -m "chore: scaffold react tailwind app"
```

### Task 2: Upload Behavior Test

**Files:**
- Create: `src/App.test.jsx`

- [ ] **Step 1: Write failing tests**

Add tests that expect the upload UI to render, accept an image file, show the filename, and clear the selection.

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test -- --run`
Expected: tests fail because `src/App.jsx` does not exist yet.

### Task 3: Upload UI Implementation

**Files:**
- Create: `src/App.jsx`

- [ ] **Step 1: Implement the UI**

Create the upload workspace with drag/drop, file picker, image preview, stable result panel, loading/error states, and mobile-safe Tailwind spacing.

- [ ] **Step 2: Run tests to verify pass**

Run: `npm test -- --run`
Expected: all tests pass.

- [ ] **Step 3: Commit UI**

Run:

```bash
git add src/App.jsx src/App.test.jsx
git commit -m "feat: add clean upload ui"
```

### Task 4: Build and Visual Verification

**Files:**
- Modify: no planned file edits unless verification finds layout problems.

- [ ] **Step 1: Build**

Run: `npm run build`
Expected: Vite completes production build without errors.

- [ ] **Step 2: Start dev server**

Run: `npm run dev -- --host 127.0.0.1`
Expected: local server URL is printed.

- [ ] **Step 3: Inspect desktop and mobile**

Open the local URL and verify no overlapping text, broken spacing, or blank render at desktop and mobile widths.
