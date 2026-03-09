from __future__ import annotations

from fpdf import FPDF

# ---------------------------------------------------------------------------
# Text sanitisation -Helvetica is Latin-1 only
# ---------------------------------------------------------------------------

_UNICODE_MAP = {
    "\u2026": "...",   # ellipsis
    "\u2019": "'",     # right single quote
    "\u2018": "'",     # left single quote
    "\u201c": '"',     # left double quote
    "\u201d": '"',     # right double quote
    "\u2013": "-",     # en dash
    "\u2014": "--",    # em dash
    "\u2022": "*",     # bullet
    "\u00b7": "*",     # middle dot
    "\u2012": "-",     # figure dash
    "\u2015": "-",     # horizontal bar
}


def _s(text: str | None) -> str:
    """Sanitise text for Helvetica (Latin-1). Replace common Unicode, drop the rest."""
    if not text:
        return ""
    for ch, repl in _UNICODE_MAP.items():
        text = text.replace(ch, repl)
    return text.encode("latin-1", errors="replace").decode("latin-1")


# Status colours (R, G, B)
_PASS = (6, 95, 70)
_WARN = (146, 64, 14)
_FAIL = (153, 27, 27)
_PASS_BG = (209, 250, 229)
_WARN_BG = (254, 243, 199)
_FAIL_BG = (254, 226, 226)
_ACCENT = (79, 70, 229)


def _status(score: float | None, thresholds: tuple[float, float] = (80, 50)) -> str:
    if score is None:
        return "warn"
    return "pass" if score >= thresholds[0] else ("warn" if score >= thresholds[1] else "fail")


def _status_color(s: str) -> tuple[int, int, int]:
    return {"pass": _PASS, "warn": _WARN, "fail": _FAIL}.get(s, (100, 100, 100))


def _status_bg(s: str) -> tuple[int, int, int]:
    return {"pass": _PASS_BG, "warn": _WARN_BG, "fail": _FAIL_BG}.get(s, (240, 240, 240))


def _symbol(s: str) -> str:
    return {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}.get(s, "-")


class _PDF(FPDF):
    def __init__(self, url: str, created_at: str) -> None:
        super().__init__()
        self._report_url = url
        self._created_at = created_at
        self.set_margins(left=15, top=12, right=15)
        self.set_auto_page_break(auto=True, margin=18)

    def header(self) -> None:
        self.set_font("Helvetica", "", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 7, _s(f"Website Analysis  |  {self._report_url}"), align="L")
        self.ln(8)

    def footer(self) -> None:
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    # ------------------------------------------------------------------ helpers

    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*_ACCENT)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*_ACCENT)
        self.line(self.get_x(), self.get_y(), self.get_x() + 180, self.get_y())
        self.ln(4)
        self.set_text_color(30, 30, 30)

    # Badge + label columns consume 16 + 62 = 78 mm of the 180 mm page body.
    _BADGE_W = 16
    _LABEL_W = 62
    _DETAIL_W = 180 - _BADGE_W - _LABEL_W  # = 102 mm
    _KV_KEY_W = 55
    _KV_VAL_W = 180 - _KV_KEY_W           # = 125 mm

    def check_row(self, label: str, detail: str, status: str) -> None:
        fr, fg, fb = _status_color(status)
        br, bg_g, bb = _status_bg(status)
        # Ensure we start at the left margin regardless of previous state.
        self.set_x(self.l_margin)
        y0 = self.get_y()
        self.set_fill_color(br, bg_g, bb)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(fr, fg, fb)
        self.cell(self._BADGE_W, 6, _symbol(status), fill=True, align="C")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(30, 30, 30)
        self.cell(self._LABEL_W, 6, _s(label)[:38])
        self.set_font("Helvetica", "", 9)
        self.set_text_color(70, 70, 70)
        self.multi_cell(self._DETAIL_W, 6, _s(detail)[:120] if detail else "")
        row_h = self.get_y() - y0
        if row_h < 7:
            self.ln(1)

    def kv(self, key: str, val: str, indent: int = 0) -> None:
        self.set_x(self.l_margin + indent)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(85, 85, 85)
        self.cell(self._KV_KEY_W, 6, _s(key) + ":")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(self._KV_VAL_W, 6, _s(str(val)) if val not in (None, "") else "-")

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(6, 6, "*", new_x="RIGHT", new_y="TOP")
        self.multi_cell(174, 6, _s(text)[:150], new_x="LMARGIN", new_y="NEXT")

    def spacer(self, h: int = 4) -> None:
        self.ln(h)

    # ------------------------------------------------------------------ cover

    def cover(self) -> None:
        self.add_page()
        self.ln(28)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*_ACCENT)
        self.cell(0, 7, "WEBSITE ANALYSIS REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(26, 26, 46)
        self.multi_cell(180, 11, _s(self._report_url), align="C")
        self.ln(6)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Saved  {self._created_at}", align="C", new_x="LMARGIN", new_y="NEXT")

    # ------------------------------------------------------------------ SEO

    def add_seo(self, seo: dict) -> None:
        self.add_page()
        self.section_title("SEO")

        title = seo.get("title") or ""
        tlen = len(title)
        self.check_row(
            "Title tag",
            f"{title[:70]}{'...' if len(title) > 70 else ''}  ({tlen} chars)",
            "pass" if 10 <= tlen <= 70 else ("fail" if not title else "warn"),
        )

        desc = seo.get("description") or ""
        dlen = len(desc)
        self.check_row(
            "Meta description",
            f"{desc[:80]}{'...' if len(desc) > 80 else ''}  ({dlen} chars)",
            "pass" if 50 <= dlen <= 160 else ("fail" if not desc else "warn"),
        )

        self.check_row("Canonical URL", seo.get("canonical") or "Not set",
                       "pass" if seo.get("canonical") else "warn")
        self.check_row("Robots meta", seo.get("robots_meta") or "Not set",
                       "pass" if seo.get("robots_meta") else "warn")
        self.check_row("sitemap.xml", "Found" if seo.get("sitemap_found") else "Not found",
                       "pass" if seo.get("sitemap_found") else "warn")
        self.check_row("robots.txt", "Found" if seo.get("robots_txt_found") else "Not found",
                       "pass" if seo.get("robots_txt_found") else "warn")

        sd = seo.get("structured_data", [])
        self.check_row("Structured data (JSON-LD)",
                       f"{len(sd)} item(s) found" if sd else "None found",
                       "pass" if sd else "warn")

        self.spacer()
        og = seo.get("og_tags", {})
        if og:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(30, 30, 30)
            self.cell(0, 7, "Open Graph tags", new_x="LMARGIN", new_y="NEXT")
            for k, v in list(og.items())[:8]:
                self.kv(k, str(v)[:80])

        headings = seo.get("headings", {})
        if any(headings.values()):
            self.spacer()
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(30, 30, 30)
            self.cell(0, 7, "Heading structure", new_x="LMARGIN", new_y="NEXT")
            for level in ["h1", "h2", "h3"]:
                items = headings.get(level, [])
                if items:
                    self.kv(level.upper(), f"{len(items)} -{items[0][:60]}")

    # ------------------------------------------------------------------ Performance

    def add_performance(self, perf: dict) -> None:
        self.add_page()
        self.section_title("Performance")

        score = perf.get("performance_score")
        if score is not None:
            self.check_row("PageSpeed score", f"{score} / 100",
                           _status(score, (90, 50)))
        elif perf.get("pagespeed_error"):
            self.check_row("PageSpeed", perf["pagespeed_error"][:80], "warn")

        vitals = [
            ("fcp", "First Contentful Paint", "Good < 1.8 s"),
            ("lcp", "Largest Contentful Paint", "Good < 2.5 s"),
            ("cls", "Cumulative Layout Shift", "Good < 0.1"),
            ("ttfb", "Time to First Byte", "Good < 0.8 s"),
            ("inp", "Interaction to Next Paint", "Good < 200 ms"),
            ("speed_index", "Speed Index", "Good < 3.4 s"),
        ]
        for key, label, hint in vitals:
            v = perf.get(key, {})
            if not isinstance(v, dict):
                continue
            display = v.get("display") or "-"
            vscore = v.get("score")
            self.check_row(label, f"{display}  ({hint})",
                           _status(vscore * 100 if vscore is not None else None, (90, 50)))

        res = perf.get("resources", {})
        if res:
            self.spacer()
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(30, 30, 30)
            self.cell(0, 7, "Resource summary", new_x="LMARGIN", new_y="NEXT")
            for k, label in [("scripts", "Scripts"), ("stylesheets", "Stylesheets"),
                              ("images", "Images"), ("html_size_kb", "HTML size (KB)")]:
                self.kv(label, str(res.get(k, 0)))

    # ------------------------------------------------------------------ Security

    def add_security(self, sec: dict) -> None:
        self.add_page()
        self.section_title("Security")

        self.check_row("HTTPS", "Enabled" if sec.get("https") else "Not enabled",
                       "pass" if sec.get("https") else "fail")

        headers = [
            ("hsts", "HSTS"),
            ("csp", "Content-Security-Policy"),
            ("x_frame_options", "X-Frame-Options"),
            ("x_content_type_options", "X-Content-Type-Options"),
            ("referrer_policy", "Referrer-Policy"),
            ("permissions_policy", "Permissions-Policy"),
        ]
        for key, label in headers:
            h = sec.get(key, {})
            if not isinstance(h, dict):
                continue
            present = h.get("present", False)
            note = h.get("note") or (h.get("value") or "")
            self.check_row(label, str(note)[:80], "pass" if present else "warn")

        mixed = sec.get("mixed_content_count", 0)
        self.check_row("Mixed content", f"{mixed} issue(s) found" if mixed else "None found",
                       "fail" if mixed > 0 else "pass")

        server = sec.get("server_header") or "Not disclosed"
        self.check_row("Server header", server, "warn" if sec.get("server_header") else "pass")

        cookies = sec.get("cookies", [])
        if cookies:
            self.spacer()
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(30, 30, 30)
            self.cell(0, 7, f"Cookies ({len(cookies)})", new_x="LMARGIN", new_y="NEXT")
            for c in cookies[:10]:
                name = c.get("name", "")
                flags = []
                if c.get("secure"):
                    flags.append("Secure")
                if c.get("http_only"):
                    flags.append("HttpOnly")
                if c.get("same_site"):
                    flags.append(f"SameSite={c['same_site']}")
                self.kv(name[:30], ", ".join(flags) if flags else "No flags")

    # ------------------------------------------------------------------ Technology

    def add_tech(self, tech: dict) -> None:
        self.add_page()
        self.section_title("Technology")

        cats = tech.get("categories", {})
        techs = tech.get("technologies", [])

        if cats:
            for cat, names in cats.items():
                self.set_font("Helvetica", "B", 10)
                self.set_text_color(30, 30, 30)
                self.cell(0, 7, cat, new_x="LMARGIN", new_y="NEXT")
                for name in names:
                    item = next((t for t in techs if t.get("name") == name), {})
                    version = item.get("version") or ""
                    conf = item.get("confidence") or ""
                    detail = f"{name}" + (f" {version}" if version else "") + (f"  [{conf}]" if conf else "")
                    self.bullet(detail)
                self.spacer(3)
        elif not techs:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "No technologies detected.", new_x="LMARGIN", new_y="NEXT")

    # ------------------------------------------------------------------ Accessibility

    def add_accessibility(self, a11y: dict) -> None:
        self.add_page()
        self.section_title("Accessibility")

        score = a11y.get("score", 0)
        self.check_row("Accessibility score", f"{score} / 100",
                       _status(score, (80, 50)))

        self.check_row("Language attribute",
                       f'lang="{a11y.get("lang_attribute")}"' if a11y.get("lang_present") else "Missing",
                       "pass" if a11y.get("lang_present") else "fail")

        ti = a11y.get("total_images", 0)
        ma = a11y.get("images_missing_alt", 0)
        ea = a11y.get("images_empty_alt", 0)
        self.check_row("Image alt text",
                       f"{ti} images -{ma} missing alt, {ea} empty alt" if ti else "No images found",
                       "pass" if ma == 0 and ea == 0 else ("fail" if ma > 3 or ea > 3 else "warn"))

        inp_total = a11y.get("total_inputs", 0)
        inp_miss = a11y.get("inputs_missing_label", 0)
        self.check_row("Form labels",
                       f"{inp_total} inputs -{inp_miss} missing label" if inp_total else "No inputs found",
                       "pass" if inp_miss == 0 else ("fail" if inp_miss > 3 else "warn"))

        self.check_row("Heading order",
                       "Valid" if a11y.get("heading_order_valid") else f"{len(a11y.get('heading_issues', []))} issue(s)",
                       "pass" if a11y.get("heading_order_valid") else "warn")

        landmarks = a11y.get("aria_landmarks", [])
        self.check_row("ARIA landmarks",
                       ", ".join(landmarks) if landmarks else "None detected",
                       "pass" if len(landmarks) >= 3 else ("warn" if landmarks else "fail"))

        ptab = a11y.get("positive_tabindex_count", 0)
        self.check_row("Positive tabindex",
                       "None found" if ptab == 0 else f"{ptab} element(s) -disrupts tab order",
                       "pass" if ptab == 0 else "warn")

    # ------------------------------------------------------------------ Content

    def add_content(self, content: dict) -> None:
        self.add_page()
        self.section_title("Content")

        flesch = content.get("flesch_reading_ease", 0)
        label = content.get("readability_label", "")
        self.check_row("Readability (Flesch)",
                       f"{flesch} -{label}",
                       _status(flesch, (60, 30)))

        self.spacer(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, "Content stats", new_x="LMARGIN", new_y="NEXT")
        for k, label_txt in [
            ("word_count", "Word count"),
            ("sentence_count", "Sentences"),
            ("paragraph_count", "Paragraphs"),
            ("avg_words_per_sentence", "Avg words / sentence"),
            ("content_to_html_ratio", "Content-to-HTML ratio (%)"),
        ]:
            self.kv(label_txt, str(content.get(k, "-")))

        self.spacer()
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, "Links", new_x="LMARGIN", new_y="NEXT")
        self.kv("Internal links", str(content.get("internal_links_total", 0)))
        self.kv("External links", str(content.get("external_links_total", 0)))

        broken = content.get("broken_links", [])
        self.check_row("Broken links",
                       f"{len(broken)} broken (of {content.get('internal_links_checked', 0)} checked)",
                       "pass" if not broken else ("warn" if len(broken) <= 2 else "fail"))
        for bl in broken[:5]:
            code = bl.get("status_code") or bl.get("error") or "?"
            self.bullet(f"{bl.get('url', '')[:70]}  [{code}]")

        self.spacer()
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, "Misc checks", new_x="LMARGIN", new_y="NEXT")
        self.check_row("Favicon", "Present" if content.get("has_favicon") else "Not found",
                       "pass" if content.get("has_favicon") else "warn")
        self.check_row("Meta viewport", "Present" if content.get("has_meta_viewport") else "Not found",
                       "pass" if content.get("has_meta_viewport") else "warn")

        preview = content.get("text_preview", "")
        if preview:
            self.spacer()
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(30, 30, 30)
            self.cell(0, 7, "Text preview", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(90, 90, 90)
            self.multi_cell(180, 6, _s(preview)[:400])


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_report_pdf(url: str, created_at: str, data: dict) -> bytes:
    pdf = _PDF(url=url, created_at=created_at)

    pdf.cover()

    if seo := data.get("seo"):
        pdf.add_seo(seo)
    if perf := data.get("performance"):
        pdf.add_performance(perf)
    if sec := data.get("security"):
        pdf.add_security(sec)
    if tech := data.get("tech"):
        pdf.add_tech(tech)
    if a11y := data.get("accessibility"):
        pdf.add_accessibility(a11y)
    if content := data.get("content"):
        pdf.add_content(content)

    return bytes(pdf.output())
