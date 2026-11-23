# Design system: Stolz Consulting (Hallmark, redesign full)

Locked. Tokens live in `assets/css/tokens.css`, base rules in `assets/css/base.css`, the page in `assets/css/style.css`.

## Brand (kept from the original site)
White and one beige, gold as the single accent, warm dark brown for text and the closing band. Portrait of Mag. Dr. Sabine Stolz on an offset gold rule. Source Serif 4 for headings (weight 400, roman, one colour), Inter for text, both self-hosted with Cyrillic.

## Shape: Ledger
- Hero: headline, one sentence, one primary action, portrait on columns 8 to 12.
- Figures are ledger rows (large serif numeral, hairline, plain label), never cards or counters.
- Services are an index (numbered rows with hairlines), not tiles.
- Steps: three columns, a large numeral over a hairline.
- Closing band: dark brown, the one filled gold button.
- Footer: the wordmark as a mast over contact and legal links.

## Rules
- Every colour and font through a token. No literal colours outside `tokens.css`.
- No eyebrows, no tracked capitals, no italic words in headings, no arrows glued to links, no dashes in copy.
- One primary button recipe (flat gold). Secondary actions are text links or the outline button.
- Hairlines (`--color-rule`, `--color-rule-strong`) divide, cards are avoided; `.card` is a single flat surface, never nested.
- Spacing from the `--space-*` scale; section gaps from `--section-gap*`.
- Motion: opacity and transform only, one reveal, always visible without scripting, `prefers-reduced-motion` honoured.
