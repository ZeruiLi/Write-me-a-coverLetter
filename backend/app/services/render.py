from __future__ import annotations

from io import BytesIO


def html_to_pdf(html: str, options: dict) -> bytes:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        raise RuntimeError("playwright not installed or browser missing: install and run 'playwright install chromium'") from e

    margin_cm = options.get("margin_cm", 2.0)
    page = options.get("page", "A4")
    header = (options.get("header") or {}).copy()
    header_enabled = header.get("enabled", True)
    header_name = header.get("name", "")
    header_contact = header.get("contact", "")

    header_html = ""
    if header_enabled:
        header_html = f"<div style='font-size:10px;width:100%;text-align:right'>{header_name} {header_contact}</div>"

    pdf_bytes = b""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page_ctx = browser.new_page()
        page_ctx.set_content(html, wait_until="load")
        pdf_bytes = page_ctx.pdf(
            format=page,
            margin={"top": f"{margin_cm}cm", "bottom": f"{margin_cm}cm", "left": f"{margin_cm}cm", "right": f"{margin_cm}cm"},
            display_header_footer=bool(header_html),
            header_template=header_html if header_html else None,
            footer_template="<div></div>",
            print_background=True,
        )
        browser.close()
    return bytes(pdf_bytes)

