# Prototype shelf

A single static page that lists every prototype and opens each one in place, with a back button. No build step, no backend.

```
prototype-shelf/
├── index.html          ← the shelf (edit the PROTOTYPES list at the top)
├── tools/
│   └── flatten_bundle.py    unpacks a bundled export into plain files
└── prototypes/
    ├── assets/
    │   ├── address-usability/   fonts, scripts, images
    │   ├── addons-quantity/
    │   ├── address-locator/
    │   ├── batch-description/
    │   ├── cohort-exploration/
    │   ├── saved-cart/
    │   ├── sku-reveal/
    │   ├── fbt-display-order/
    │   ├── pay-strip/
    │   ├── exam-first-teaching/
    │   └── voice-search/
    ├── thumbs/
    │   ├── address-usability.svg
    │   └── addons-quantity.svg
    ├── address-usability.html   (App)
    ├── addons-quantity.html     (App)
    ├── address-locator.html     (App)
    ├── batch-description.html   (App)
    ├── cohort-exploration.html  (App)
    ├── saved-cart.html          (App)
    ├── sku-reveal.html          (App)
    ├── fbt-display-order.html   (Admin)
    ├── pay-strip.html           (App)
    ├── voice-search.html        (App)
    └── exam-first-teaching.html (App)
```

## Add a prototype

1. Drop the HTML file into `prototypes/`.
2. Add one entry to the `PROTOTYPES` array near the top of `index.html`:

```js
{
  slug: "paywall-v3",                        // becomes the URL: /#p=paywall-v3
  title: "Paywall — three-tier",
  snippet: "Three tiers, annual preselected", // one mono line: what the screen actually does
  description: "One or two sentences on what this tests.",
  file: "prototypes/paywall-v3.html",
  platform: "App",                           // "App" | "Web" | "Admin" — drives the filter
  frame: "phone",                            // "phone" or "wide"
  thumb: "prototypes/thumbs/paywall-v3.svg", // optional — see below
  tags: ["Monetisation"],                    // free-text labels shown on the card
  updated: "26 Aug 2026"
}
```

`snippet` and `description` do different jobs, so keep them distinct: the snippet is the mechanic — what a reviewer will see and touch — while the description is the problem being tested. Both are searchable.

## Bundled exports — run them through the flattener

Prototype exports from the design tool ship every asset as base64 inside one HTML file and mint `blob:` URLs for them at runtime. Browsers block blob-URL scripts in nested and sandboxed frames and on `file://`, which produces:

```
Warning: [bundle] resource failed to load: SCRIPT blob-request://blob-...
```

`tools/flatten_bundle.py` fixes this permanently by writing the assets out as real files and rewriting the page to reference them, so there is nothing left to unpack:

```bash
python3 tools/flatten_bundle.py ~/Downloads/My_Export.html \
        prototypes/my-prototype.html \
        prototypes/assets/my-prototype
```

It also sets `window.__resources` to the extracted React and ReactDOM copies, so the page doesn't reach out to unpkg.com either. All listed prototypes have been flattened. Run any new export through this before adding it to the shelf.

## Card images

By default a card renders the real prototype in a scaled-down iframe, so the thumbnail can never go stale. To use a static image instead, add `thumb` pointing at a PNG, JPG or SVG in `prototypes/thumbs/`; the full prototype still opens normally in the viewer. Address Usability and Add Ons Quantity currently use static images. Delete the `thumb` line from an entry to switch that card back to a live preview.

The shelf has 19 built prototypes and 12 remaining pipeline ideas. The PW Growth Roadmap appears only through the Roadmap pill; other App prototypes appear under both All and App. Search Expansion adds an always-available frosted search button to the batch listing. Filter Experiments keeps filters one tap away while scrolling and covers the former “Students don't notice filters” pipeline idea. Saved Cart keeps explored batches and the selected plan ready to buy, with a persistent bag and direct order-summary path. Best-Fit Batch Reveal uses onboarding answers to pop up the single best-matching batch over the filtered listing, with enrolment straight from the pop-up. PW Upsell Sheet pitches the next plan at checkout, with Basic-to-Infinity/Pro and Infinity-to-Pro paths. Batch Steal Deals offers low-ticket digital products in the cart and skips address entry for digital-only purchases. Counsellor Offer Nudge contains two switchable versions.

## Filters

The platform chips are **All · App · Web · Admin**; Pipeline scrolls to the planned ideas, and Roadmap shows only the PW Growth Roadmap card. Each prototype's `platform` decides which platform chip it appears under, except the roadmap, which is exclusive to its pill. The pipeline shares the platform filters and search; its count reflects the matching ideas.

`tags` are separate: they're descriptive labels on the card (and searchable), not filters.

## How it behaves

- **Card previews are live.** Each card renders the real prototype in a scaled-down iframe, so the thumbnail never goes stale. `frame: "phone"` renders it at 430px wide; `"wide"` at 1240px.
- **Opening is in-place.** Clicking a card sets the URL to `#p=slug` and drops the prototype into a full-screen viewer. The back button in the viewer, the browser back button, and <kbd>Esc</kbd> all return to the shelf.
- **Every prototype is shareable.** Send someone `yoursite.vercel.app/#p=doubt-chat` and it opens straight into that prototype.
- **Preview width.** Prototypes open at full width in the viewer; the Phone view has been removed.
- **Search.** `/` focuses the search box.
- **Pipeline.** The Pipeline chip jumps to the 14 ideas still in progress.

## Run locally

```bash
npx serve .
```

Opening `index.html` directly off the filesystem mostly works, but a local server avoids browser restrictions on nested local files.

## Deploy to Vercel

Static site, nothing to configure.

**CLI**

```bash
npm i -g vercel
cd prototype-shelf
vercel          # preview URL
vercel --prod   # production
```

**Dashboard** — push the folder to a Git repo, then in Vercel: New Project → import the repo → Framework preset **Other** → leave build command and output directory empty → Deploy.

Or drag the folder onto vercel.com/new for a one-off deploy.

## Notes

- Keep prototype filenames stable — `slug` is what people bookmark, but the file path is what the iframe loads.
- Prototypes can use their own CSS, fonts and CDN scripts. They're fully isolated in the iframe, so nothing leaks into the shelf styling.
- If a card shows "Preview unavailable", the path in `file` doesn't match a real file. Paths are case-sensitive on Vercel.
