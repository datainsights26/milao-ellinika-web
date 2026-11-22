# Μιλάω ελληνικά – web version

Beginner Greek course (21 lessons + 4 revision quizzes) following the order of *Πες το Ελληνικά A1–A2*.
Open it at **https://datainsights26.github.io/milao-ellinika-web/** – no login needed.
On a phone, use **Add to Home Screen** to get an app icon. Progress and notes are saved on each device.

## How it's built
- `index.html` – the whole course (one page, offline fonts in `fonts/`).
- Every push to `main` runs `.github/workflows/build-site.yml`, which records each phrase as an MP3
  with the Piper Greek voice (`el_GR-rapunzelina-low`, MIT licence, CC0 training data) and publishes the site to the `gh-pages` branch.
- After changing any Greek text, run `node tools/list_phrases.js > phrases.json` so new phrases get recorded.
