# RKNP Football AI MVP — Demo Order

## Recommended Presentation Flow

1. **Show `main_candidate_sheet.jpg`**  
   Explain: "Coach must visually confirm the target player (green box) before trusting the report."

2. **Show `main_overlay.mp4`**  
   Explain: "Short-clip tracking with bounding box overlay on the selected player."

3. **Show `main_crop.mp4`**  
   Explain: "Player-centered crop showing the tracked player's movement in isolation."

4. **Show `main_contact_sheet.jpg`**  
   Explain: "Visual timeline of sampled frames to verify tracking consistency."

5. **Show `main_report.md`**  
   Explain: "Markdown report with image-space metrics, quality gate result, and LLM explanation."

6. **Show backup files only if needed**  
   (`backup_overlay.mp4`, `backup_crop.mp4`, etc.) — Secondary demo case.

7. **Show `failure_overlay.mp4` and `failure_crop.mp4`**  
   Explain: "Failure case demonstrating limitations when tracking is unreliable."

8. **Show `two_players.png`**  
   Explain: "Difficult case with two players in similar jerseys — illustrates identity ambiguity risk."

9. **Explain limitations and future work**  
   Refer to `research_report.md` and `jury_qa.md` for detailed answers.

---

## Main Message

> **This is not full-match football understanding.**  
> This is a **short-clip single-player analysis MVP** with:
> - Visual evidence (overlay video, crop video, contact sheet)
> - Image-space metrics (visibility %, trusted tracking %, speed outliers, occlusion risk)
> - Quality gate (high/medium/low reliability with explicit reasons)
> - Honest limitations (no km/h, no xG, no pass accuracy, no heatmaps, no full-match tracking)
> - LLM as explanation layer only (does NOT watch video or invent CV facts)

---

## File Reference

| Purpose | File |
|---------|------|
| Main demo overlay | `main_overlay.mp4` |
| Main demo crop | `main_crop.mp4` |
| Main candidate sheet | `main_candidate_sheet.jpg` |
| Main contact sheet | `main_contact_sheet.jpg` |
| Main report (readable) | `main_report.md` |
| Main report (data) | `main_report.json` |
| Backup overlay | `backup_overlay.mp4` |
| Backup crop | `backup_crop.mp4` |
| Backup candidate sheet | `backup_candidate_sheet.jpg` |
| Backup contact sheet | `backup_contact_sheet.jpg` |
| Failure overlay | `failure_overlay.mp4` |
| Failure crop | `failure_crop.mp4` |
| Failure contact sheet | `failure_contact_sheet.jpg` |
| Failure report | `failure_report.json` |
| Two-player case | `two_players.png` |
| Raw cluster frame | `raw_cluster_frame51.jpg` |
| Two-player summary | `two_player_tracking_summary.md` |
| Defense script | `defense_script.md` |
| Jury Q&A | `jury_qa.md` |
| Research report | `research_report.md` |
| Asset index | `demo_asset_index.md` |
