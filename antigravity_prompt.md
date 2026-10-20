# PROMPT FOR ANTIGRAVITY — "3P DWP" Instagram-style Reel (school assignment)

You are a video editor + motion designer working on my Mac. Build an educational 9:16 reel from my two files, using FFmpeg and Whisper locally. **Ask me before installing anything** (only free/open-source tools). **Show me a storyboard confirmation and 3 caption-check frames before the final render.**

---

## 0. Files

- `ElevenLabs_2026-10-20T05_32_19_Caleb_ivc_sp100_s50_sb75_v4.mp3` — voiceover (my ElevenLabs voice clone). **This is the ONLY audio source.** 95.79 s, 44.1 kHz, integrated loudness −22.9 LUFS.
- `WhatsApp Video 2026-10-20 at 12.41.13.mp4` — talking-head video of me. 480×854, 30 fps, 99.84 s. Me in a black varsity jacket with a blue "U", holding a small speaker like a mic, white wall/door background. **Mute its audio completely.**

Known issues:
- Low resolution (480×854 → 1080×1920 is 2.25× upscale). Use a good scaler (lanczos) + light sharpening, and keep punch-ins small (max ~108–112%).
- Lip-sync will NOT match the MP3 (different audio + cuts + reordering). So my face should mostly appear as a **cut-out (green-screen style) over graphics or a picture-in-picture**, not long full-screen lip-sync shots. Full-screen face only for short punchy moments.

---

## 1. Assignment rubric (hard requirements — do not break these)

Task: Educational reel analysing **3P of service marketing (People, Process, Physical Evidence)** for an Event Organizer. My case: **Ismaya Live / Djakarta Warehouse Project (DWP)**.

Must include:
1. Attention-grabbing **hook** at the start.
2. Explanation of People, Process, Physical Evidence in the context of a service.
3. Case analysis with **at least 1 specific piece of evidence per P**. **When evidence is discussed, show it on screen** (news image, data screenshot, or website page) **with the source name visible**.
4. **Sharp opinion at the end**: which P matters most and why (my answer: **Process**).
5. Format **9:16 portrait**, duration **80–90 s, NEVER over 90 s**.
6. Engaging animation/editing; visuals that aid understanding (images, icons, illustrations, clips, simple graphics).
7. **End with a "Sumber" (Sources) slide for 3–5 s** listing title/source name, year, and link/short note. **This slide counts inside the 90 s.**
8. Not posted to social media → background music can be burned into the file.

---

## 2. Editing spec

**Audio (MP3 only)**
- Transcribe the MP3 with Whisper locally, language Indonesian, **word-level timestamps**:
  `whisper "<mp3>" --language id --model small --word_timestamps True --output_format json`
  (or faster-whisper with `word_timestamps=True`). Use `medium` if `small` mis-hears words.
- Cut filler words, false starts, and **pauses longer than 0.3 s** (shorten them to ~0.10–0.12 s). **Cut only between words** (in silence gaps, with ~40–60 ms padding and short 5–10 ms crossfades) so nothing sounds clipped.
- Light cleanup: gentle denoise (e.g. `afftdn` or `arnndn`), high-pass ~80 Hz.
- **Speed up the speech** (`atempo`, pitch-preserving) so voice + 3–5 s source slide ≤ 90 s total. Expect ~1.05–1.07×. Target final length **~88 s**.
- Loudness: **−14 LUFS integrated, true peak −1 dBTP** (two-pass `loudnorm`), measured on the final mix incl. music.
- Background music: royalty-free/CC0 (or generated), ducked ~18 dB under voice (sidechain). Energetic electronic/festival vibe fitting DWP.
- SFX (royalty-free/generated): whoosh on transitions, pop on caption/graphic entries, cash register, barcode/RFID beep, glass crack, bass hit/drop, error buzz, chain clank.

**Pause map from my earlier analysis** (silencedetect −35 dB, d=0.3; format = silence_end s, duration s) — re-verify with Whisper:
1.357 0.331 · 7.734 0.610 · 10.714 0.513 · 13.667 0.428 · 19.257 0.385 · 20.893 0.513 · 24.149 0.301 · 29.155 0.413 · 35.601 0.475 · 37.272 0.374 · 45.651 0.446 · 51.069 0.397 · 53.161 0.321 · 57.026 0.396 · 67.276 0.357 · 68.967 0.365 · 72.864 0.376 · 76.994 0.342 · 82.048 0.353 · 90.774 0.420
(~20 pauses → cutting them saves ~5–6 s, so ~90 s of speech before speed-up.)

**Hook rule:** the strongest line must land in the **first three words**. Move it to the front as a cold open. Strongest line = the closing line *"…hiburan jutaan rupiah bisa berubah jadi bencana dalam hitungan menit."* (if the exact wording differs in the MP3, use the transcript). Since it moves to the front, the video ends on the Process verdict + Sources slide.

**Video**
- Output **1080×1920, H.264 (libx264, high profile, yuv420p), 30 fps, CRF ~18, AAC 320k / 48 kHz**, `+faststart`.
- Crop to 9:16 with **my face centered** (face detection/tracking, smoothed).
- **Punch in slightly on each key point** (~105–110%, quick ease).
- Cut-out of me ("green screen") using a free segmentation tool (e.g. MediaPipe selfie segmentation, rembg, or Robust Video Matting) — ask before installing. Place me over animated backgrounds.
- You don't always need to show my face — cut to animations/graphics that physically show what I'm saying (search/prompt boxes, people buying tickets, checkout screens, receipts, wristbands, gates, crowds).

**Captions (burned in)**
- **2–3 words at a time**, synced to word timings.
- **Bold white with thick black outline** (heavy sans: e.g. Montserrat/Inter Black/Poppins ExtraBold). Lower-middle third, safe from UI edges.
- **Most important word per phrase in yellow** (#FFD60A); **danger/failure words in red** (#FF2D3D); **Process/system words in blue** (#1E6BFF).
- Pop-in animation (scale 80→105→100%, ~120 ms).
- Fix Whisper spelling errors against the script below (names: Ismaya Live, Djakarta Warehouse Project, DWP, Garuda Land, RFID, Liaison Officer).

**Color system:** yellow #FFD60A (money, key words), blue #1E6BFF (Process/systems), red #FF2D3D (failure/warnings), black / off-white backgrounds.

**Recurring motif:** a **concert ticket stub** that stays on screen through the reel. It gets stamped at each P (PEOPLE ✓ yellow, PROCESS ✓ blue, PHYSICAL ✓ red) and is **torn in half** in the verdict. Also a small **3P progress bar** pinned at the top after the intro.

---

## 3. Script (approximate voiceover content — use the Whisper transcript as truth)

1. Hook: "Pernah kepikiran nggak, kenapa orang rela bayar jutaan rupiah buat produk yang nggak bisa dipegang dan langsung habis dalam semalam?"
2. Intro: "Jawabannya ada di 3P Service Marketing: People, Process, dan Physical Evidence. Kita bedah langsung di balik layar Ismaya Live, promotor di balik megahnya Djakarta Warehouse Project."
3. People: "Pertama, People. Bisnis konser bergantung penuh pada manusia di balik layar: mulai dari sound engineer bersertifikasi, kru panggung, sampai Liaison Officer. Sikap sigap tim medis dan keramahan LO menentukan rasa aman penonton serta kenyamanan artis kelas dunia."
4. Process: "Kedua, Process. Alurnya dimulai dari pembelian tiket online, penukaran wristband berbasis RFID, hingga manajemen alur keluar-masuk puluhan ribu orang di venue. Proses tapping RFID yang cepat memotong antrean panjang dan mencegah kekacauan di gerbang masuk."
5. Physical Evidence: "Ketiga, Physical Evidence. Karena jasa tidak berwujud, kepercayaan dibangun lewat bukti fisik: megahnya panggung ikonik Garuda-Bot, visual laser kelas dunia, wristband fisik, hingga feed Instagram yang rapi sebagai portofolio sebelum pembeli memutuskan bertransaksi."
6. Interlock: "Ketiganya saling mengunci: sistem RFID canggih (Process) nggak ada artinya kalau staf gerbang (People) lambat, dan kemegahan panggung (Physical Evidence) jadi sia-sia kalau arus kerumunan berantakan."
7. Verdict: "Dari ketiga P, yang paling menentukan hidup-matinya EO konser adalah Process. Panggung semegah apa pun dan staf seramah apa pun langsung runtuh reputasinya jika sistem ticketing jebol atau manajemen kerumunan gagal total."
8. Closing line (→ moved to cold open): "Tanpa proses yang solid, hiburan jutaan rupiah bisa berubah jadi bencana dalam hitungan menit."

---

## 4. Research findings & fact corrections (already verified)

| Script says | Verified fact | Handling |
|---|---|---|
| "Garuda-Bot" stage | The DWP main stage is **"Garuda Land"**, inspired by the Garuda of Indonesia's coat of arms, with lasers, pyro, fireworks (Dancing Astronaut, 2015) | On-screen text/caption says **"Garuda Land"** (voice can't be changed) |
| DWP 2023 | 2023 (15th edition) was at **GWK Cultural Park, Bali**, Dec 8–10. 2024 was at **JIExpo Kemayoran, Jakarta**. DWP 2026: Dec 11–13, Jakarta | Don't label Jakarta visuals as 2023 |
| "Tiket 2 juta" | DWP 2026 3-Day Pass GA (Early Entry) from **Rp 2,1 juta** (detik). DWP 2024 GA daily from Rp 800 rb, VIP daily from Rp 1,75 juta (JPNN) | Use Rp 2,1 juta in hook graphic |
| RFID wristband at DWP | **Not verified.** Verified: official Ismaya guideline — e-voucher is exchanged for a **wristband, which is your entry ticket** (DWP19 Exchange Guideline) | Show "e-voucher → wristband" as DWP fact; label RFID as "praktik industri" (industry practice) |
| Sources "Ismaya Live Official Documentation & Event Architecture (2023)" and "DWP Post-Event Report & Ticketing Flow (2023)" | **Could not be found — likely fabricated** | **Do NOT show them.** Use the verified list below |

**Evidence to show on screen (one per P + hook):**
- Hook: DWP 2026 price Rp 2,1 juta — detik.com — https://www.detik.com/pop/music/d-8642700/siap-siap-dwp-2026-balik-lagi-ke-jakarta
- **People:** DWP 2024 — Polri deployed **450 personnel**; **18 police officers** allegedly extorted Malaysian attendees; DWP issued an official statement; 20 officers went through ethics hearings (3 dismissed, 17 demoted). Insight: even people the EO doesn't employ shape the customer's judgment of the service.
  - JPNN — https://www.jpnn.com/news/penonton-diperas-polisi-dwp-2024-sampaikan-pernyataan-resmi
  - Kompas TV — https://www.kompas.tv/nasional/566920/daftar-20-anggota-polisi-disanksi-buntut-kasus-pemerasan-dwp-3-dipecat
- **Process:** Official Ismaya DWP19 Exchange Guideline — e-voucher exchanged for wristband = entry ticket — https://www.ismaya.com/storage/app/media/live/dwp19-exchangeguidelineenglish.pdf
- **Physical Evidence:** Garuda Land main stage — Dancing Astronaut (2015) — https://dancingastronaut.com/2015/12/djakarta-warehouse-project-2015 ; Wikipedia (venues, history, Garuda Land image) — https://en.wikipedia.org/wiki/Djakarta_Warehouse_Project
- Theory: Zeithaml, Bitner & Gremler (2018), *Services Marketing: Integrating Customer Focus Across the Firm*, 7th ed., McGraw-Hill.

**Screenshots:** take real screenshots of these pages (via browser) and show them in the evidence moments with the outlet name + year clearly visible. If a page can't be loaded, build a clean "article card" (outlet logo-free, headline, outlet name, date, URL) — but real screenshots are preferred.

**Footage:** Only use footage/images that are free to use (e.g. Wikimedia Commons with CC license + credit). Do not rip Instagram/YouTube clips. Otherwise everything is motion graphics.

---

## 5. Storyboard (target ~88 s total; timings after cuts + speed-up)

**0:00–0:04 · COLD OPEN (moved strongest line)**
VO: "…hiburan jutaan rupiah bisa berubah jadi bencana dalam hitungan menit."
Visual: black → red glitch flash → crowd silhouette made of laser lines; a countdown "00:59 → 00:00" races; screen cracks.
Captions: **JUTAAN RUPIAH** (yellow) → **BENCANA** (red, shake). SFX: sub-bass hit → glass crack.

**0:04–0:10 · QUESTION**
VO: "Pernah kepikiran nggak, kenapa orang rela bayar jutaan rupiah…"
Visual: my cut-out slides in over a blue grid; a search/prompt box types *"kenapa tiket konser mahal?"*. SFX: keyboard clicks.

**0:10–0:16 · THE INVISIBLE PRODUCT**
VO: "…buat produk yang nggak bisa dipegang dan langsung habis dalam semalam?"
Visual: checkout UI **"DWP 2026 · 3-Day Pass · Rp 2.100.000 → BAYAR"**, cursor taps; a receipt prints: *"Barang fisik: 0 · Durasi: 1 malam"*; receipt burns. Small source tag: "detik.com, 2026". SFX: cash register, fizz.

**0:16–0:24 · FRAMEWORK**
VO: "Jawabannya ada di 3P… People, Process, Physical Evidence."
Visual: three tiles slam in on each word — PEOPLE (yellow), PROCESS (blue), PHYSICAL EVIDENCE (red). 3P progress bar locks to the top. Ticket stub appears.

**0:24–0:28 · CASE**
VO: "…Ismaya Live, promotor di balik Djakarta Warehouse Project."
Visual: typewriter "DWP · Ismaya Live · sejak 2008"; abstract Garuda wings made of laser lines.

**0:28–0:42 · P1 PEOPLE**
Visual: punch-in on me → icon cards flip in: 🎚 Sound Engineer · 🧰 Kru Panggung · 🪪 LO · ⛑ Tim Medis. On "keramahan LO" an artist chat bubble "Thanks team 🙏". **Evidence moment:** JPNN/Kompas TV screenshot — "DWP 2024: 450 personel Polri; 18 oknum diduga memeras penonton" with source name + year. Text: "People di luar timmu pun ikut menentukan reputasi". Stamp: PEOPLE ✓ (yellow).

**0:42–0:56 · P2 PROCESS**
Visual: animated flow: phone "WAR TIKET" countdown → **e-voucher → wristband** exchange → wristband tap (blue ring + beep) → gate turns green → crowd dots flow. Split screen: "ANTRE MANUAL" (red jammed dots) vs "TAP & MASUK" (smooth). **Evidence moment:** Ismaya DWP19 Exchange Guideline screenshot with "ismaya.com · 2019". Tag "RFID = praktik industri". Stamp: PROCESS ✓ (blue).

**0:56–1:10 · P3 PHYSICAL EVIDENCE**
Visual: Garuda Land stage rebuilt in laser/firework motion graphics (or a CC-licensed photo) labelled **"Garuda Land"**; glowing wristband spinning in close-up; an Instagram-style 3×3 grid filling tile by tile → cursor taps "Beli". **Evidence moment:** Dancing Astronaut 2015 screenshot + Wikipedia. Caption **BUKTI FISIK** (yellow). Stamp: PHYSICAL ✓ (red).

**1:10–1:18 · INTERLOCK**
Visual: the three tiles form a triangle linked with chains. Pull "People" ("staf lambat" turns red) → triangle collapses; reset; pull "Process" ("kerumunan kacau") → collapses. SFX: chain clank, crash.

**1:18–1:25 · VERDICT (the punch)**
Visual: me full-screen with a hard punch-in (only big face moment); a blue crown drops onto **PROCESS** → **"THE KINGMAKER"** slams in. On "sistem ticketing jebol" a red error modal **"503 · Server Overload"**; the ticket stub tears in half. SFX: bass drop, error buzz.

**1:25–1:29 · SUMBER SLIDE (3–5 s, mandatory)**
Clean static slide, title "Sumber":
1. detik.com (2026) — "Siap-siap! DWP 2026 Balik Lagi ke Jakarta" — harga tiket
2. JPNN (2024) — "Penonton Diperas Polisi, DWP 2024 Sampaikan Pernyataan Resmi"
3. Kompas TV (2025) — Sanksi 20 anggota polisi kasus DWP
4. Ismaya Live (2019) — DWP19 Exchange Guideline (ismaya.com)
5. Dancing Astronaut (2015) — DWP 2015 review / Garuda Land
6. Wikipedia — Djakarta Warehouse Project
7. Zeithaml, Bitner & Gremler (2018) — *Services Marketing*, 7th ed.
(Verify each date/title when taking screenshots; fix if different.)

---

## 6. Workflow & checkpoints

1. Check what's installed (ffmpeg, whisper/faster-whisper, segmentation tool, fonts). **Ask before installing anything.**
2. Transcribe with word timings → show me the transcript + list of proposed cuts (fillers, false starts, pauses).
3. Build the cut + sped-up + cleaned voice track; report final duration (must leave room for the 3–5 s source slide, total ≤ 90 s).
4. Map the storyboard to real timestamps → **show me the timed storyboard before rendering.**
5. Build graphics/animations, captions, cut-outs, music, SFX.
6. **Render 3 still frames** (one with a yellow keyword, one evidence moment, one verdict) **so I can check the captions before you finish.**
7. Final export 1080×1920 H.264, verify: duration 80–90 s, −14 LUFS (±0.5), true peak ≤ −1 dBTP, no MP4 audio present.

---

## 7. What was already tried in a previous attempt (cloud container, Claude Code)

- Probed files (specs above), made a contact sheet (confirmed talking head, face roughly centered, upper third), measured pauses and loudness (−22.9 LUFS).
- Researched the topic (findings in section 4).
- Installed `faster-whisper` + `rembg` in a Python venv, but the **cloud network blocked model downloads** (Hugging Face, GitHub); a third-party npm repackage of Whisper-small was blocked by the safety policy. **No transcription, cuts, or renders were produced.** Running locally on my Mac avoids these problems.
