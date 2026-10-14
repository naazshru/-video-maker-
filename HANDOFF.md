# Handoff for the next Claude session (local machine)

User: makes cinematic 3D launch trailers for USHVIKA products ("Nature's Goodness. For You").
Talk to the user in Hindi. They want it quick, beautiful, cinematic.

## Hard rules from the user
- **Never change the product, pack or label.** Only real photos are used (scaled/cropped only).
- Films play back-to-back: the **brand intro is only in the first film (Rose Tea)**. Later films
  skip it and spend the time on **benefits**. Order-number end card only once at the very end.
- Hindi female voice-over (vidIQ voice "Sarah", id EXAVITQu4vr4xnSDxMaL), same voice for every product.
- Don't invent claims: benefits come from the label or the user.

## Status
| Film | Folder | State |
|---|---|---|
| Rose Tea Premix | trailer/ | done → Ushvika_Rose_Tea_Trailer.mp4 (music only, no VO yet) |
| Rose Jelly | jelly/ | done → Ushvika_Rose_Jelly.mp4 |
| Rose Badam Shake Premix | badam/ | done → Ushvika_Rose_Badam.mp4 |
| Rose Petal Twist (rose milk shake, pouch) | twist/ | done → Ushvika_Rose_Petal_Twist.mp4 (benefit cards not yet confirmed by user) |

## Render
```
npm install && npx playwright install chromium     # once; also needs ffmpeg on PATH
node build.mjs --gpu badam twist                  # GPU, opens a Chromium window
```
Outputs go to out/. Copy to repo root as Ushvika_Rose_Badam.mp4 / Ushvika_Rose_Petal_Twist.mp4 and commit.

## Next ideas the user agreed to / may want
- Final combined brand film: Tea (with intro) → Jelly → Badam → Twist → one order-number end card (81462-06677).
- Hindi VO for Rose Tea to match the others.
- More products: user sends a "character sheet" (8 views + top + bottom) per product.

## How a new product is added
1. `python3 tools/crop_sheet.py <product>/src/sheet.png <product>/tex` (sheet must be a transparent PNG; views left→right, top→bottom = 45° steps around the pack, then TOP, BOTTOM).
2. Copy the closest index.html, set window.PRODUCT (dur, cardRot per benefit, hero camera), texts.
3. music.json → `python3 trailer/score.py <p>/music.wav <p>/music.json`
4. VO via vidIQ → <p>/vo_raw.mp3, split lines into <p>/vo_segments.txt → `trailer/mix.sh <p> <dur>`
5. `node build.mjs --gpu <p>`
