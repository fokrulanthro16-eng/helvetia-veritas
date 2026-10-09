"""
HelvetiaVeritas - Automated High-Resolution Screenshot Capture Script
Captures 5 high-resolution (1920x1080) screenshots using Playwright Chromium:
1. '01_dashboard_full.png' - Full page overview of the dashboard.
2. '02_cantonal_analysis.png' - Focused screenshot of the cantonal heuristic analysis and confidence chart.
3. '03_dialect_transformation.png' - Focused screenshot of the dialect input vs standardized German text.
4. '04_legal_articles_audit.png' - Focused screenshot of the identified Swiss legal articles and cryptographic audit certificate.
5. '05_api_swagger_docs.png' - Full view of the FastAPI Swagger documentation at http://localhost:8000/docs.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

def capture_all_screenshots():
    # Ensure screenshots directory exists
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target screenshots directory: {SCREENSHOTS_DIR}")

    with sync_playwright() as p:
        # Launch Chromium with 1920x1080 viewport and high DPI
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0
        )
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. Dashboard Overview
        # -------------------------------------------------------------
        dashboard_url = "http://localhost:8000/#/analysen"
        print(f"\n[1/5] Navigating to {dashboard_url}...")
        page.goto(dashboard_url, wait_until="networkidle")

        # Wait for baseline analysis data to populate
        page.wait_for_timeout(2000)
        page.wait_for_selector("#normalized-output")

        # Capture 01_dashboard_full.png (High-Res 1920x1080 Viewport)
        p1 = SCREENSHOTS_DIR / "01_dashboard_full.png"
        page.screenshot(path=str(p1), full_page=False)
        print(f"  -> Saved 01_dashboard_full.png ({os.path.getsize(p1):,} bytes)")

        # -------------------------------------------------------------
        # 2. Focused Cantonal Heuristic Analysis & Confidence Chart
        # -------------------------------------------------------------
        print("\n[2/5] Capturing Cantonal Heuristic Analysis card (#canton-card)...")
        canton_card = page.locator("#canton-card")
        canton_card.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        p2 = SCREENSHOTS_DIR / "02_cantonal_analysis.png"
        canton_card.screenshot(path=str(p2))
        print(f"  -> Saved 02_cantonal_analysis.png ({os.path.getsize(p2):,} bytes)")

        # -------------------------------------------------------------
        # 3. Dialect Input vs Standardized German Text
        # -------------------------------------------------------------
        print("\n[3/5] Capturing Dialect Input vs Standardized German Text...")
        # Bounding box spanning dialect input card, telemetry, and output card
        input_card = page.locator(".dialect-input-card")
        output_card = page.locator(".output-card")
        input_card.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        box_input = input_card.bounding_box()
        box_output = output_card.bounding_box()

        if box_input and box_output:
            x = min(box_input["x"], box_output["x"]) - 10
            y = min(box_input["y"], box_output["y"]) - 10
            width = max(box_input["x"] + box_input["width"], box_output["x"] + box_output["width"]) - x + 20
            height = (box_output["y"] + box_output["height"]) - y + 10
            p3 = SCREENSHOTS_DIR / "03_dialect_transformation.png"
            page.screenshot(
                path=str(p3),
                clip={"x": max(x, 0), "y": max(y, 0), "width": width, "height": height}
            )
        else:
            p3 = SCREENSHOTS_DIR / "03_dialect_transformation.png"
            output_card.screenshot(path=str(p3))
        print(f"  -> Saved 03_dialect_transformation.png ({os.path.getsize(p3):,} bytes)")

        # -------------------------------------------------------------
        # 4. Identified Legal Articles & Cryptographic Audit Certificate
        # -------------------------------------------------------------
        print("\n[4/5] Capturing Swiss Legal Articles & Cryptographic Audit Certificate...")
        statutes_card = page.locator(".statutes-card")
        attestation_card = page.locator("#attestation-card")
        attestation_card.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Capture attestation certificate card and statutes side-by-side
        p4 = SCREENSHOTS_DIR / "04_legal_articles_audit.png"
        box_stat = statutes_card.bounding_box()
        box_att = attestation_card.bounding_box()
        if box_stat and box_att:
            min_y = min(box_stat["y"], box_att["y"]) - 10
            max_y = max(box_stat["y"] + box_stat["height"], box_att["y"] + box_att["height"]) + 10
            min_x = min(box_stat["x"], box_att["x"]) - 10
            max_x = max(box_stat["x"] + box_stat["width"], box_att["x"] + box_att["width"]) + 10
            page.screenshot(
                path=str(p4),
                clip={"x": max(min_x, 0), "y": max(min_y, 0), "width": max_x - min_x, "height": max_y - min_y}
            )
        elif box_att:
            attestation_card.screenshot(path=str(p4))
        else:
            statutes_card.screenshot(path=str(p4))
        print(f"  -> Saved 04_legal_articles_audit.png ({os.path.getsize(p4):,} bytes)")

        # -------------------------------------------------------------
        # 5. FastAPI Swagger Docs at http://localhost:8000/docs
        # -------------------------------------------------------------
        docs_url = "http://localhost:8000/docs"
        print(f"\n[5/5] Navigating to {docs_url}...")
        page.goto(docs_url, wait_until="networkidle")
        page.wait_for_selector(".swagger-ui")
        page.wait_for_timeout(1000)

        p5 = SCREENSHOTS_DIR / "05_api_swagger_docs.png"
        page.screenshot(path=str(p5), full_page=False)
        print(f"  -> Saved 05_api_swagger_docs.png ({os.path.getsize(p5):,} bytes)")

        browser.close()

    print("\n=======================================================")
    print("ALL 5 SCREENSHOTS CAPTURED AND SAVED SUCCESSFULLY!")
    print(f"Location: {SCREENSHOTS_DIR}")
    print("=======================================================")

if __name__ == "__main__":
    capture_all_screenshots()
