# Gladius CombatWear Logo — SVG Code

## How to Use This

When you need to update the logo on the website:

1. **Get the SVG code** — either from a designer or by describing what you want
2. **Copy the `<svg>` block** from the code example below
3. **Send it to me** with a screenshot showing what it should look like
4. **I'll embed it** into the website immediately

## Current Correct Logo — SVG Code

```svg
<svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <!-- Shield outline — golden stroke -->
  <path d="M 25 15 L 75 15 L 75 50 Q 75 85 50 110 Q 25 85 25 50 Z" 
        fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
  
  <!-- Cross inside shield -->
  <!-- Vertical blade -->
  <rect x="46" y="25" width="8" height="65" fill="currentColor" rx="2"/>
  
  <!-- Horizontal crossguard -->
  <rect x="33" y="52" width="34" height="8" fill="currentColor" rx="2"/>
</svg>
```

## How to Replace the Logo

If you have a new logo SVG:

1. Extract just the `<svg>...</svg>` part
2. Make sure it has `viewBox="0 0 100 120"` (or similar ratio)
3. Replace `currentColor` with `currentColor` (it will inherit the gold/white color from CSS)
4. Send me the code block
5. I'll update both:
   - `gladius/index.html` (nav logo)
   - `gladius/styles.css` (card logo mark)

## Logo Requirements

- **Format**: SVG code block (between `<svg>` and `</svg>`)
- **Color**: Use `currentColor` so it works in gold (nav) and white (cards)
- **Viewbox**: Any aspect ratio is fine, I'll adjust the sizing
- **Include**: The complete, clean SVG code

## Example — If You Get Logo from Designer

Ask them for the SVG code and it will look like:

```svg
<svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M 25 15 L 75 15 L 75 50 Q 75 85 50 110 Q 25 85 25 50 Z" fill="none" stroke="currentColor" stroke-width="4"/>
  <rect x="46" y="25" width="8" height="65" fill="currentColor"/>
  <rect x="33" y="52" width="34" height="8" fill="currentColor"/>
</svg>
```

Just copy that whole block and send it — I'll have it live in 2 minutes.

---

## To Fix This Now

If you have access to the actual logo file (PNG, JPG, or SVG):

**Option A — SVG file**
- Send me the `.svg` file and I'll extract the code

**Option B — PNG/JPG image**
- I can have a designer convert it to SVG, or
- You can use an online converter: https://www.pngtosvg.com/ or https://www.autotracer.org/
- Then send me the SVG code

**Option C — Describe it precisely**
- Shield shape (rounded bottom, straight top)
- Cross inside (vertical line + horizontal line)
- Colors and proportions
- I'll build the SVG from scratch

Which option works best for you?
