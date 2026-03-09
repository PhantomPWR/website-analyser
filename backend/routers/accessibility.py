import re

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()


class ImageAltIssue(BaseModel):
    src: str
    issue: str  # "missing_alt" | "empty_alt"


class FormLabelIssue(BaseModel):
    element: str
    input_type: str | None
    issue: str


class HeadingIssue(BaseModel):
    tag: str
    text: str
    issue: str


class AccessibilityResult(BaseModel):
    lang_attribute: str | None
    lang_present: bool
    # Images
    total_images: int
    images_missing_alt: int
    images_empty_alt: int
    image_issues: list[ImageAltIssue]
    # Forms
    total_inputs: int
    inputs_missing_label: int
    form_issues: list[FormLabelIssue]
    # Headings
    heading_order_valid: bool
    heading_issues: list[HeadingIssue]
    # ARIA
    aria_roles_count: int
    aria_labels_count: int
    aria_landmarks: list[str]
    # Skip links
    skip_link_present: bool
    # Tabindex
    positive_tabindex_count: int
    # Score
    score: int
    issues_total: int


def _check_heading_order(soup) -> tuple[bool, list[HeadingIssue]]:
    issues: list[HeadingIssue] = []
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    prev_level = 0
    h1_count = 0

    for h in headings:
        level = int(h.name[1])
        text = h.get_text(strip=True)[:80]

        if h.name == "h1":
            h1_count += 1
            if h1_count > 1:
                issues.append(HeadingIssue(tag=h.name, text=text, issue="Multiple H1 tags found"))

        if prev_level > 0 and level > prev_level + 1:
            issues.append(HeadingIssue(
                tag=h.name,
                text=text,
                issue=f"Skipped heading level (H{prev_level} → H{level})",
            ))
        prev_level = level

    if h1_count == 0:
        issues.append(HeadingIssue(tag="h1", text="", issue="No H1 tag found"))

    return len(issues) == 0, issues


def _check_images(soup) -> tuple[int, int, int, list[ImageAltIssue]]:
    imgs = soup.find_all("img")
    missing = 0
    empty = 0
    issues: list[ImageAltIssue] = []

    for img in imgs:
        src = img.get("src", "")[:100]
        if "alt" not in img.attrs:
            missing += 1
            issues.append(ImageAltIssue(src=src, issue="missing_alt"))
        elif img.get("alt", "").strip() == "":
            empty += 1
            issues.append(ImageAltIssue(src=src, issue="empty_alt"))

    return len(imgs), missing, empty, issues[:20]


def _check_form_inputs(soup) -> tuple[int, int, list[FormLabelIssue]]:
    inputs = soup.find_all(["input", "select", "textarea"])
    skippable_types = {"hidden", "submit", "button", "reset", "image"}
    issues: list[FormLabelIssue] = []
    missing = 0

    for inp in inputs:
        itype = inp.get("type", "text").lower()
        if itype in skippable_types:
            continue

        input_id = inp.get("id")
        has_label = False

        if input_id:
            label = soup.find("label", attrs={"for": input_id})
            has_label = label is not None

        has_aria_label = bool(inp.get("aria-label") or inp.get("aria-labelledby"))
        has_title = bool(inp.get("title"))

        if not has_label and not has_aria_label and not has_title:
            missing += 1
            tag = inp.name
            issues.append(FormLabelIssue(
                element=tag,
                input_type=itype if tag == "input" else None,
                issue="No associated label, aria-label, or title",
            ))

    return len(inputs), missing, issues[:20]


def _check_aria(soup) -> tuple[int, int, list[str]]:
    roles = soup.find_all(attrs={"role": True})
    aria_labels = soup.find_all(attrs={"aria-label": True})

    landmark_roles = {"banner", "main", "navigation", "contentinfo", "complementary", "search", "form", "region"}
    found_landmarks: list[str] = []

    for el in roles:
        role = el.get("role", "")
        if role in landmark_roles and role not in found_landmarks:
            found_landmarks.append(role)

    # Also check semantic HTML5 landmarks
    semantic_map = {
        "header": "banner", "main": "main", "nav": "navigation",
        "footer": "contentinfo", "aside": "complementary", "section": "region",
    }
    for tag, role in semantic_map.items():
        if soup.find(tag) and role not in found_landmarks:
            found_landmarks.append(role)

    return len(roles), len(aria_labels), sorted(found_landmarks)


def _compute_score(
    lang_present: bool,
    img_missing: int,
    img_empty: int,
    total_imgs: int,
    form_missing: int,
    total_inputs: int,
    heading_valid: bool,
    skip_link: bool,
    positive_tabindex: int,
) -> int:
    score = 100
    if not lang_present:
        score -= 10
    if total_imgs > 0:
        bad_ratio = (img_missing + img_empty) / total_imgs
        score -= int(bad_ratio * 30)
    if total_inputs > 0:
        label_ratio = form_missing / total_inputs
        score -= int(label_ratio * 25)
    if not heading_valid:
        score -= 15
    if not skip_link:
        score -= 5
    if positive_tabindex > 0:
        score -= min(positive_tabindex * 2, 10)
    return max(0, min(100, score))


@router.get("/accessibility", response_model=AccessibilityResult)
async def analyse_accessibility(url: str = Query(..., description="URL to analyse")):
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    soup = page.soup

    # lang attribute
    html_tag = soup.find("html")
    lang = html_tag.get("lang") if html_tag else None
    lang_present = bool(lang and lang.strip())

    # Images
    total_imgs, img_missing, img_empty, image_issues = _check_images(soup)

    # Forms
    total_inputs, form_missing, form_issues = _check_form_inputs(soup)

    # Headings
    heading_valid, heading_issues = _check_heading_order(soup)

    # ARIA
    aria_roles, aria_labels, landmarks = _check_aria(soup)

    # Skip link — first link href starts with #
    first_link = soup.find("a", href=re.compile(r"^#"))
    skip_link = first_link is not None

    # Positive tabindex (anti-pattern)
    positive_tabindex = len([
        el for el in soup.find_all(tabindex=True)
        if el.get("tabindex", "0").lstrip("-").isdigit() and int(el.get("tabindex", "0")) > 0
    ])

    score = _compute_score(
        lang_present, img_missing, img_empty, total_imgs,
        form_missing, total_inputs, heading_valid, skip_link, positive_tabindex,
    )

    issues_total = (
        (0 if lang_present else 1)
        + img_missing + img_empty
        + form_missing
        + len(heading_issues)
        + positive_tabindex
    )

    return AccessibilityResult(
        lang_attribute=lang,
        lang_present=lang_present,
        total_images=total_imgs,
        images_missing_alt=img_missing,
        images_empty_alt=img_empty,
        image_issues=image_issues,
        total_inputs=total_inputs,
        inputs_missing_label=form_missing,
        form_issues=form_issues,
        heading_order_valid=heading_valid,
        heading_issues=heading_issues,
        aria_roles_count=aria_roles,
        aria_labels_count=aria_labels,
        aria_landmarks=landmarks,
        skip_link_present=skip_link,
        positive_tabindex_count=positive_tabindex,
        score=score,
        issues_total=issues_total,
    )
