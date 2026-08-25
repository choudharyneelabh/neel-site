# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page "coming soon" landing site for Neel, deployed on Netlify. There is no build step and no framework — `index.html` is served as-is, and `netlify/functions/subscribe.js` runs as a Netlify serverless function.

## Architecture

- `index.html` — the entire site: markup, CSS (in a `<style>` block), and JS (in a `<script>` block) in one file. The JS drives a cursor-following spotlight effect and the email signup form.
- `netlify/functions/subscribe.js` — a Netlify function (ESM default export, standard `Request`/`Response`) that the signup form POSTs to at `/.netlify/functions/subscribe`. It validates the email, inserts it into a Supabase `subscribers` table via `@supabase/supabase-js`, and treats a Postgres unique-constraint violation (code `23505`) as an "already subscribed" success rather than an error.
- The function reads `SUPABASE_URL` and `SUPABASE_SECRET_KEY` from environment variables (set in the Netlify dashboard, not in code).

## Running locally

There's no dev server or build script configured in `package.json`. To exercise the Netlify function locally, use the Netlify CLI (`netlify dev`), which serves `index.html` and proxies `/.netlify/functions/*` to the local function runtime — this also requires `SUPABASE_URL` and `SUPABASE_SECRET_KEY` to be set (e.g. via `netlify env` or a local `.env`).

There are no tests or lint configuration in this repo.
