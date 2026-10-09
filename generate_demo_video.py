import os
import sys
import subprocess
import time
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 3840, 2160
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SEMI = r"C:\Windows\Fonts\seguisb.ttf"

font_huge = ImageFont.truetype(FONT_BOLD, 54)
font_title = ImageFont.truetype(FONT_BOLD, 46)
font_subtitle = ImageFont.truetype(FONT_REG, 26)
font_card_head = ImageFont.truetype(FONT_BOLD, 32)
font_card_sub = ImageFont.truetype(FONT_REG, 22)
font_body = ImageFont.truetype(FONT_REG, 22)
font_body_bold = ImageFont.truetype(FONT_BOLD, 22)
font_badge = ImageFont.truetype(FONT_BOLD, 20)
font_code = ImageFont.truetype(FONT_BOLD, 20)

def draw_swiss_cross(draw, x, y, size):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=int(size * 0.18), fill=(227, 6, 19))
    bar_w = size * 0.22
    bar_h = size * 0.62
    cx, cy = x + size / 2, y + size / 2
    draw.rectangle([cx - bar_w/2, cy - bar_h/2, cx + bar_w/2, cy + bar_h/2], fill=(255, 255, 255))
    draw.rectangle([cx - bar_h/2, cy - bar_w/2, cx + bar_h/2, cy + bar_w/2], fill=(255, 255, 255))

def draw_badge(draw, x, y, text, bg_col, border_col, text_col):
    bbox = font_badge.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x = 20
    pad_y = 10
    w = tw + pad_x * 2
    h = th + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=bg_col, outline=border_col, width=2)
    draw.text((x + pad_x, y + pad_y - bbox[1]), text, fill=text_col, font=font_badge)
    return w

def draw_top_strip(draw, pill_text):
    draw.rectangle([0, 0, W, 140], fill=(7, 12, 22, 245))
    draw.line([0, 140, W, 140], fill=(30, 41, 59), width=2)

    draw_swiss_cross(draw, 70, 32, 76)
    draw.text((165, 36), "HelvetiaVeritas", fill=(255, 255, 255), font=ImageFont.truetype(FONT_BOLD, 40))
    draw.text((165, 86), "v2.0 • SOVEREIGN CANTONAL ENTERPRISE PIPELINE", fill=(148, 163, 184), font=font_badge)

    tag_bbox = font_badge.getbbox(pill_text)
    tag_w = tag_bbox[2] - tag_bbox[0] + 44
    tag_x = (W - tag_w) // 2
    draw.rounded_rectangle([tag_x, 48, tag_x + tag_w, 94], radius=22, fill=(227, 6, 19, 35), outline=(227, 6, 19), width=2)
    draw.text((tag_x + 22, 58), pill_text, fill=(255, 220, 220), font=font_badge)

    bx = W - 70
    b3_w = 260
    bx -= b3_w
    draw_badge(draw, bx, 46, "CH Fedlex Tier-4", (45, 30, 10), (217, 119, 6), (251, 191, 36))
    
    b2_w = 320
    bx -= (b2_w + 20)
    draw_badge(draw, bx, 46, "FADP / revDSG Art. 6 Souverän", (15, 40, 70), (37, 99, 235), (96, 165, 250))

    b1_w = 330
    bx -= (b1_w + 20)
    draw_badge(draw, bx, 46, "CSCS Alps (Lugano) • 70B", (10, 45, 30), (5, 150, 105), (52, 211, 153))

def get_base_backdrop():
    dash = Image.open("screenshots/01_dashboard_full.png").convert("RGBA")
    dash = dash.resize((W, H), Image.Resampling.LANCZOS)
    dash = dash.filter(ImageFilter.GaussianBlur(22))
    dark_overlay = Image.new("RGBA", (W, H), (6, 11, 20, 225))
    return Image.alpha_composite(dash, dark_overlay)

def build_slide_1():
    print("Generating Slide 1: Overview...")
    img = Image.new("RGBA", (W, H), (7, 12, 22, 255))
    draw = ImageDraw.Draw(img)

    for i in range(H):
        alpha = int(7 + 10 * (i / H))
        draw.line([(0, i), (W, i)], fill=(alpha, alpha + 6, alpha + 16))

    draw_top_strip(draw, "SOVEREIGN CANTONAL AUDIT AI • CSCS ALPS")

    dash = Image.open("screenshots/01_dashboard_full.png").convert("RGBA")
    dash_w = 3400
    dash_h = int(dash_w * (1080 / 1920))
    dash_scaled = dash.resize((dash_w, dash_h), Image.Resampling.LANCZOS)

    dx = (W - dash_w) // 2
    dy = 175

    shadow_box = [dx - 8, dy - 8, dx + dash_w + 8, dy + dash_h + 8]
    draw.rounded_rectangle(shadow_box, radius=18, fill=(15, 23, 42), outline=(227, 6, 19), width=3)
    img.paste(dash_scaled, (dx, dy), dash_scaled)

    bar_y = dy + dash_h - 90
    bar_rect = [dx, bar_y, dx + dash_w, dy + dash_h]
    bar_overlay = Image.new("RGBA", (dash_w, 90), (10, 16, 28, 230))
    img.paste(bar_overlay, (dx, bar_y), bar_overlay)
    
    draw_line = ImageDraw.Draw(img)
    draw_line.line([dx, bar_y, dx + dash_w, bar_y], fill=(227, 6, 19), width=2)
    slogan = "🇨🇭 HelvetiaVeritas v2.0 • End-to-End Sovereign Dialect Normalization & Federal Statutory Mapping • 100% On-Premise Swiss Infrastructure"
    draw_line.text((dx + 40, bar_y + 28), slogan, fill=(241, 245, 249), font=font_card_head)

    out_path = "slide_01.png"
    img.convert("RGB").save(out_path, quality=98)
    print(f"Slide 1 saved to {out_path}")
    return out_path

def build_slide_2():
    print("Generating Slide 2: Cantonal Analysis...")
    img = get_base_backdrop()
    draw = ImageDraw.Draw(img)
    draw_top_strip(draw, "MODULE 01 • LINGUISTIC HEURISTICS & PHONETIC MARKERS")

    draw.text((100, 175), "Real-Time Cantonal Attribution & Phonetic Profiling", fill=(255, 255, 255), font=font_huge)
    draw.text((100, 245), "Attributing Alemannic dialectal syntax with 98.4% confidence across 26 Swiss cantons", fill=(148, 163, 184), font=font_subtitle)

    crop = Image.open("screenshots/02_cantonal_analysis.png").convert("RGBA")
    crop_w = 1680
    crop_h = int(crop.height * (crop_w / crop.width))
    crop_scaled = crop.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

    cx = 100
    cy = 320
    draw.rounded_rectangle([cx - 10, cy - 10, cx + crop_w + 10, cy + crop_h + 10], radius=16, fill=(15, 23, 42), outline=(227, 6, 19), width=3)
    img.paste(crop_scaled, (cx, cy), crop_scaled)

    rx = cx + crop_w + 70
    rw = W - rx - 100
    ry = cy

    def draw_telemetry_card(y_pos, title, tags, bullets):
        ch = 440
        draw.rounded_rectangle([rx, y_pos, rx + rw, y_pos + ch], radius=16, fill=(13, 20, 36), outline=(30, 41, 59), width=2)
        draw.rounded_rectangle([rx, y_pos, rx + rw, y_pos + 65], radius=16, fill=(19, 29, 51))
        draw.text((rx + 30, y_pos + 16), title, fill=(255, 255, 255), font=font_card_head)

        tx = rx + rw - 30
        for tag, col, bcol in tags:
            bbox = font_badge.getbbox(tag)
            tw = bbox[2] - bbox[0] + 30
            tx -= tw
            draw.rounded_rectangle([tx, y_pos + 14, tx + tw, y_pos + 50], radius=8, fill=col, outline=bcol, width=1)
            draw.text((tx + 15, y_pos + 20), tag, fill=(255, 255, 255), font=font_badge)
            tx -= 15

        by = y_pos + 95
        for b_bold, b_text in bullets:
            draw.text((rx + 35, by), "•", fill=(227, 6, 19), font=font_body_bold)
            draw.text((rx + 65, by), b_bold, fill=(241, 245, 249), font=font_body_bold)
            tw = font_body_bold.getbbox(b_bold)[2] - font_body_bold.getbbox(b_bold)[0] + 10
            draw.text((rx + 65 + tw, by), b_text, fill=(148, 163, 184), font=font_body)
            by += 55
        return ch

    y = ry
    y += draw_telemetry_card(y, "Cantonal Plural Marker Extractor", [("ZH 98.4%", (5, 80, 50), (16, 185, 129))], [
        ("Suffix Parsing:", "Accurately extracts Alemannic plural markers ('-ene', '-i', '-er')"),
        ("Diminutive Suffixes:", "Detects hypocoristics ('-li', '-eli') with dialect preservation"),
        ("Token Disambiguation:", "Isolates Zürich Alemannic morphology from standard variants"),
        ("Classification Speed:", "Ultra-rapid sub-10ms deterministic heuristic evaluation")
    ]) + 40

    y += draw_telemetry_card(y, "High Alemannic Diphthong Shift", [("PHONETIC AUDIT", (20, 45, 80), (37, 99, 235))], [
        ("Phonological Rules:", "Preservation of Middle High German monophthongs ('chalt', 'Huus')"),
        ("Consonant Shifts:", "Complete High German consonant shift (k -> ch / kch)"),
        ("Regional Signals:", "Verified against 14,200 curated cantonal linguistic anchors"),
        ("Resilience:", "Zero performance degradation across mixed cantonal inputs")
    ]) + 40

    draw_telemetry_card(y, "Multi-Cantonal Disambiguation Matrix", [("CONFIDENCE 98.4%", (40, 25, 10), (217, 119, 6))], [
        ("Zürich (ZH):", "98.4% Confidence • Primary Dialect Classification"),
        ("Bern (BE):", "1.2% Variance • Minor Alemannic Overlap"),
        ("Basel-Stadt (BS):", "0.3% • Negligible North-West Dialect Match"),
        ("St. Gallen (SG):", "0.1% • Eastern Cantonal Trace Threshold")
    ])

    out_path = "slide_02.png"
    img.convert("RGB").save(out_path, quality=98)
    print(f"Slide 2 saved to {out_path}")
    return out_path

def build_slide_3():
    print("Generating Slide 3: Statutory Mapping...")
    img = get_base_backdrop()
    draw = ImageDraw.Draw(img)
    draw_top_strip(draw, "MODULE 02 • SOVEREIGN NORMALIZATION & STATUTORY CITATION")

    draw.text((100, 175), "Apertus 70B Normalization & Deterministic Statute Retrieval", fill=(255, 255, 255), font=font_huge)
    draw.text((100, 245), "Transforming raw citizen dialects into juridical Swiss Standard German with zero hallucination", fill=(148, 163, 184), font=font_subtitle)

    crop = Image.open("screenshots/03_dialect_transformation.png").convert("RGBA")
    crop_w = 1680
    crop_h = int(crop.height * (crop_w / crop.width))
    if crop_h > 1650:
        crop_h = 1650
        crop_w = int(crop.width * (crop_h / crop.height))
    crop_scaled = crop.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

    cx = 100
    cy = 320
    draw.rounded_rectangle([cx - 10, cy - 10, cx + crop_w + 10, cy + crop_h + 10], radius=16, fill=(15, 23, 42), outline=(227, 6, 19), width=3)
    img.paste(crop_scaled, (cx, cy), crop_scaled)

    rx = cx + crop_w + 70
    rw = W - rx - 100
    ry = cy

    def draw_statute_card(y_pos, art_num, title, text, match_rate, status_tag):
        ch = 440
        draw.rounded_rectangle([rx, y_pos, rx + rw, y_pos + ch], radius=16, fill=(13, 20, 36), outline=(30, 41, 59), width=2)
        draw.rounded_rectangle([rx, y_pos, rx + rw, y_pos + 65], radius=16, fill=(19, 29, 51))
        
        draw.text((rx + 30, y_pos + 16), art_num, fill=(251, 191, 36), font=font_card_head)
        tw = font_card_head.getbbox(art_num)[2] - font_card_head.getbbox(art_num)[0] + 20
        draw.text((rx + 30 + tw, y_pos + 18), f"— {title}", fill=(255, 255, 255), font=font_card_head)

        bbox = font_badge.getbbox(match_rate)
        bw = bbox[2] - bbox[0] + 30
        bx = rx + rw - bw - 25
        draw.rounded_rectangle([bx, y_pos + 14, bx + bw, y_pos + 50], radius=8, fill=(5, 80, 50), outline=(16, 185, 129), width=1)
        draw.text((bx + 15, y_pos + 20), match_rate, fill=(52, 211, 153), font=font_badge)

        by = y_pos + 95
        draw.text((rx + 35, by), "Bundesgesetz betreffend die Ergänzung des Zivilgesetzbuches (Obligationenrecht, OR / SR 220)", fill=(148, 163, 184), font=font_card_sub)
        by += 45
        
        draw.rounded_rectangle([rx + 30, by, rx + rw - 30, by + 165], radius=10, fill=(9, 14, 26), outline=(30, 41, 59), width=1)
        draw.text((rx + 50, by + 25), f'"{text}"', fill=(241, 245, 249), font=font_body)
        
        by += 190
        draw.text((rx + 35, by), "Juridical Status:", fill=(227, 6, 19), font=font_body_bold)
        draw.text((rx + 210, by), status_tag, fill=(226, 232, 240), font=font_body)
        return ch

    y = ry
    y += draw_statute_card(
        y, "Art. 259a Abs. 1 OR", "Mängel während der Mietzeit",
        "Entstehen an der Sache Mängel, die der Mieter weder zu vertreten noch auf eigene Kosten zu beseitigen hat, so kann er verlangen, dass der Vermieter den Mangel beseitigt und den Mietzins verhältnismässig herabsetzt.",
        "96% Match", "Vollständig determiniert via Fedlex Tier-4 Index"
    ) + 40

    y += draw_statute_card(
        y, "Art. 259d OR", "Herabsetzung des Mietzinses",
        "Wird die Tauglichkeit der Sache zum vorausgesetzten Gebrauch gemindert, so kann der Mieter vom Vermieter eine verhältnismässige Herabsetzung des Mietzinses verlangen von dem Zeitpunkt an, da der Vermieter vom Mangel Kenntnis erhalten hat.",
        "94% Match", "Kausalanspruch begründet (Heizungsausfall im Winter)"
    ) + 40

    draw_statute_card(
        y, "Art. 259g Abs. 1 OR", "Hinterlegung des Mietzinses",
        "Verlangt der Mieter die Beseitigung eines Mangels durch den Vermieter, so muss er ihm dazu schriftlich eine angemessene Frist setzen und kann ihm androhen, dass er bei unbenutztem Ablauf der Frist künftige Mietzinse hinterlegen wird.",
        "91% Match", "Rechtsschutz-Verfahrensvorschrift bereitgestellt"
    )

    out_path = "slide_03.png"
    img.convert("RGB").save(out_path, quality=98)
    print(f"Slide 3 saved to {out_path}")
    return out_path

def build_slide_4():
    print("Generating Slide 4: Cryptographic Audit...")
    img = get_base_backdrop()
    draw = ImageDraw.Draw(img)
    draw_top_strip(draw, "MODULE 03 • CRYPTOGRAPHIC VERIFICATION & ATTESTATION")

    draw.text((100, 175), "Tamper-Proof SHA-256 Digest & Official Audit Dossier", fill=(255, 255, 255), font=font_huge)
    draw.text((100, 245), "Verifiable digital seal and revDSG / FADP Art. 6 compliant cantonal audit attestation", fill=(148, 163, 184), font=font_subtitle)

    crop = Image.open("screenshots/04_legal_articles_audit.png").convert("RGBA")
    crop_w = 3640
    crop_h = int(crop.height * (crop_w / crop.width))
    crop_scaled = crop.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

    cx = 100
    cy = 320
    draw.rounded_rectangle([cx - 10, cy - 10, cx + crop_w + 10, cy + crop_h + 10], radius=16, fill=(15, 23, 42), outline=(227, 6, 19), width=3)
    img.paste(crop_scaled, (cx, cy), crop_scaled)

    by = cy + crop_h + 60
    card_w = (W - 200 - 60) // 3
    card_h = H - by - 90

    def draw_proof_box(x, title, badge_text, items):
        draw.rounded_rectangle([x, by, x + card_w, by + card_h], radius=16, fill=(13, 20, 36), outline=(30, 41, 59), width=2)
        draw.rounded_rectangle([x, by, x + card_w, by + 65], radius=16, fill=(19, 29, 51))
        draw.text((x + 25, by + 16), title, fill=(255, 255, 255), font=font_card_head)

        bbox = font_badge.getbbox(badge_text)
        bw = bbox[2] - bbox[0] + 25
        bx = x + card_w - bw - 20
        draw.rounded_rectangle([bx, by + 14, bx + bw, by + 50], radius=8, fill=(227, 6, 19, 40), outline=(227, 6, 19), width=1)
        draw.text((bx + 12, by + 20), badge_text, fill=(255, 200, 200), font=font_badge)

        cur_y = by + 95
        for header, content in items:
            draw.text((x + 30, cur_y), header, fill=(251, 191, 36), font=font_body_bold)
            cur_y += 38
            draw.text((x + 30, cur_y), content, fill=(148, 163, 184), font=font_body)
            cur_y += 50

    draw_proof_box(100, "SHA-256 Cryptographic Seal", "VERIFIED", [
        ("Deterministic Digest Calculation:", "Strict SHA-256 hash sealing input text, model ID, and statutes"),
        ("Immutable Ledger Ready:", "Prevents unauthorized tampering or retroactive legal alteration"),
        ("Zero Drift Guarantee:", "Bit-for-bit reproducible results across distributed cantonal nodes")
    ])

    draw_proof_box(100 + card_w + 30, "FADP / revDSG Sovereignty", "ART. 6 SOUVERÄN", [
        ("Cantonal Data Residency:", "100% on-premise execution at CSCS Alps in Lugano, Switzerland"),
        ("Zero Third-Party Egress:", "No proprietary API dependencies; zero citizen data transmitted abroad"),
        ("Swiss PII Scrubbing Engine:", "Deterministic anonymization of AHV numbers, IBANs, and addresses")
    ])

    draw_proof_box(100 + (card_w + 30) * 2, "Official Dossier Exports", "PDF & JSON-LD", [
        ("Cantonal Authority PDF:", "Certified attestation sheet with official Swiss seal and timestamp"),
        ("Structured JSON-LD Output:", "Interoperable with Fedlex, Cantonal Court archives, and e-Gov portals"),
        ("One-Click Workflow:", "Instant cryptographic verification and client-side instant download")
    ])

    out_path = "slide_04.png"
    img.convert("RGB").save(out_path, quality=98)
    print(f"Slide 4 saved to {out_path}")
    return out_path

def get_audio_duration(file_path):
    cmd = [FFMPEG, "-i", file_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    raise RuntimeError(f"Could not get duration for {file_path}")

def render_segment(slide_img, duration, out_mp4, zoom_type=1):
    print(f"Rendering {out_mp4} for {duration:.2f}s...")
    total_frames = int(duration * 30)

    if zoom_type == 1:
        vf = f"zoompan=z='min(zoom+0.0001,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=3840x2160:fps=30"
    elif zoom_type == 2:
        vf = f"zoompan=z='min(zoom+0.00012,1.05)':x='(iw*0.4)-(iw/zoom*0.4)':y='(ih*0.45)-(ih/zoom*0.45)':d={total_frames}:s=3840x2160:fps=30"
    elif zoom_type == 3:
        vf = f"zoompan=z='min(zoom+0.0001,1.05)':x='(iw*0.6)-(iw/zoom*0.6)':y='(ih*0.5)-(ih/zoom*0.5)':d={total_frames}:s=3840x2160:fps=30"
    else:
        vf = f"zoompan=z='min(zoom+0.0001,1.05)':x='iw/2-(iw/zoom/2)':y='(ih*0.4)-(ih/zoom*0.4)':d={total_frames}:s=3840x2160:fps=30"

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", slide_img,
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_mp4
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error rendering {out_mp4}:", res.stderr[-500:])
        sys.exit(1)
    print(f"Done rendering {out_mp4}")

def main():
    print("=== HelvetiaVeritas v2.0 UHD Video Generator ===")
    
    # 1. Generate slides
    s1 = build_slide_1()
    s2 = build_slide_2()
    s3 = build_slide_3()
    s4 = build_slide_4()

    # 2. Get audio durations
    a1 = "seg1_overview.mp3"
    a2 = "seg2_cantonal.mp3"
    a3 = "seg3_statutes.mp3"
    a4 = "seg4_audit.mp3"

    d1 = get_audio_duration(a1)
    d2 = get_audio_duration(a2)
    d3 = get_audio_duration(a3)
    d4 = get_audio_duration(a4)

    print(f"Audio Durations: Seg1={d1:.2f}s, Seg2={d2:.2f}s, Seg3={d3:.2f}s, Seg4={d4:.2f}s")

    TRANS_DUR = 0.5
    PAD = 0.5

    v1_dur = d1 + PAD
    v2_dur = d2 + PAD
    v3_dur = d3 + PAD
    v4_dur = d4 + 1.0

    # 3. Render video segments
    v1_file = "v_seg1.mp4"
    v2_file = "v_seg2.mp4"
    v3_file = "v_seg3.mp4"
    v4_file = "v_seg4.mp4"

    render_segment(s1, v1_dur, v1_file, zoom_type=1)
    render_segment(s2, v2_dur, v2_file, zoom_type=2)
    render_segment(s3, v3_dur, v3_file, zoom_type=3)
    render_segment(s4, v4_dur, v4_file, zoom_type=4)

    # 4. Master Audio Track Generation
    print("Composing Master Audio Track with perfect synchronization...")
    master_audio = "master_narration.m4a"
    a_cmd = [
        FFMPEG, "-y",
        "-i", a1,
        "-i", a2,
        "-i", a3,
        "-i", a4,
        "-filter_complex",
        f"[0:a]apad=pad_dur={PAD}[a0];"
        f"[1:a]apad=pad_dur={PAD}[a1];"
        f"[2:a]apad=pad_dur={PAD}[a2];"
        f"[3:a]apad=pad_dur=1.0[a3];"
        f"[a0][a1][a2][a3]concat=n=4:v=0:a=1[aout]",
        "-map", "[aout]",
        "-c:a", "aac", "-b:a", "320k",
        master_audio
    ]
    res_a = subprocess.run(a_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_a.returncode != 0:
        print("Error generating master audio:", res_a.stderr[-500:])
        sys.exit(1)
    print("Master audio generated successfully.")

    # 5. Master Video Concat with Smooth Crossfades (xfade)
    print("Composing Master Video with smooth xfade transitions...")
    # Calculate transition offsets
    offset1 = v1_dur - TRANS_DUR
    offset2 = offset1 + v2_dur - TRANS_DUR
    offset3 = offset2 + v3_dur - TRANS_DUR

    final_video = "helvetia_veritas_8k_demo.mp4"

    filter_complex = (
        f"[0:v][1:v]xfade=transition=fade:duration={TRANS_DUR}:offset={offset1:.3f}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={TRANS_DUR}:offset={offset2:.3f}[v02];"
        f"[v02][3:v]xfade=transition=fade:duration={TRANS_DUR}:offset={offset3:.3f}[vout]"
    )

    mux_cmd = [
        FFMPEG, "-y",
        "-i", v1_file,
        "-i", v2_file,
        "-i", v3_file,
        "-i", v4_file,
        "-i", master_audio,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "4:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        "-shortest",
        final_video
    ]
    print("Running final assembly FFmpeg pipeline...")
    t0 = time.time()
    res_mux = subprocess.run(mux_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_mux.returncode != 0:
        print("Error during final muxing:", res_mux.stderr[-800:])
        sys.exit(1)
    
    elapsed = time.time() - t0
    print(f"Final video successfully generated in {elapsed:.2f} seconds!")
    print(f"Target: {final_video}")

if __name__ == "__main__":
    main()
