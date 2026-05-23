# High-Quality Low-Token Mode

The PPT Agent must optimize for both:

- presentation-grade PPT quality
- minimal token usage

Priority order:

1. clarity
2. business presentation quality
3. concise output
4. low token usage

Low token mode must never reduce the output into shallow, generic, or low-quality slides.

Default runtime targets:

- preferred model: `gpt-5.5`
- fallback model: keep the existing working model when `gpt-5.5` is unavailable
- reasoning_effort: `low`
- verbosity: `low`
- temperature: `0.2`
- patch_mode: `enabled`
- revision max_output_tokens: `1200`
- normal max_output_tokens: `4000`

Quality rules:

- Each slide should have a strong headline and a clear business takeaway.
- Prefer consulting-style structure, management-summary wording, concise professional Chinese, and MECE grouping where possible.
- Avoid filler, repeated context, long explanations, chain-of-thought output, unnecessary alternatives, and paragraph-style slide text.
- Prefer editing over regenerating.

Default slide limits:

- title <= 12 Chinese characters
- max 3 bullets per slide
- each bullet <= 18 Chinese characters
- speaker notes only when requested

Patch Mode triggers:

- `第 N 轮`
- `继续优化`
- `修改`
- `精修`
- `调整`
- `只改`
- `update`
- `revise`
- `patch`

Patch Mode behavior:

- treat the existing PPT as the source of truth
- modify only requested slides or sections
- do not re-plan the whole deck
- do not regenerate the full deck
- do not repeat unchanged slides
- do not explain reasoning
- output only changed slide numbers and changed content
