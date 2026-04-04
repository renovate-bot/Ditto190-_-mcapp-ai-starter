---
name: corporate-brand-guidelines
description: Applies consistent corporate branding standards to all documents ensuring colors, fonts, layouts, and messaging align with organizational brand guidelines
license: MIT
compatibility:
  - min-version: '1.0'
    platforms:
      - claude
      - copilot
allowed-tools:
  - read_file
  - write_file
metadata:
  source: claude-cookbooks
  category: brand-management
  domain: corporate-communications
  organization: Acme Corporation
  tags:
    - branding
    - document-formatting
    - design-standards
    - compliance
  authors:
    - name: Anthropic Team
      github: anthropics
---

# Corporate Brand Guidelines Skill

Ensures all generated documents and communications adhere to corporate brand standards for consistent, professional, legally compliant communication.

## Overview

This skill encodes Acme Corporation's brand standards, enabling Claude and GitHub Copilot to automatically apply correct branding across all document types: PowerPoint presentations, Excel reports, PDF documents, and web content.

## Brand Identity

**Company**: Acme Corporation  
**Tagline**: "Innovation Through Excellence"  
**Industry**: Technology Solutions  
**Founded**: 1985 | **Headquarters**: San Francisco, CA

## Visual Standards

### Color Palette

**Primary Colors**
- Acme Blue: #0066CC (RGB 0, 102, 204) - Headers, primary actions
- Acme Navy: #003366 (RGB 0, 51, 102) - Body text, secondary elements
- White: #FFFFFF - Light backgrounds, contrast

**Secondary Colors**
- Success Green: #28A745 - Positive values, growth
- Warning Amber: #FFC107 - Warnings, attention needed
- Error Red: #DC3545 - Errors, losses, negatives
- Neutral Gray: #6C757D - Muted text, disabled states
- Light Gray: #F8F9FA - Backgrounds, separators

**Usage Rules**
- Acme Blue for primary calls-to-action
- Navy for body copy (exceeds WCAG AA contrast standards)
- Maintain 4.5:1 contrast ratio minimum for accessibility
- Never use other colors for primary branding

### Typography

**Primary Font**: Segoe UI, system-ui, -apple-system, sans-serif

**Font Hierarchy**
- H1: 32pt, Bold, Acme Blue (#0066CC)
- H2: 24pt, Semibold, Acme Navy (#003366)
- H3: 18pt, Semibold, Acme Navy (#003366)
- Body: 11pt, Regular, Acme Navy (#003366)
- Caption: 9pt, Regular, Neutral Gray (#6C757D)

**Best Practices**
- Minimum 11pt body text for readability
- 1.5x line spacing for readability
- Generous margins (0.5 - 1 inch)
- Consistent heading styles throughout

### Logo Usage

**Placement**: Top-left corner on first page/slide
**Size**: 120px width (maintain aspect ratio)
**Clear Space**: Minimum 20px padding on all sides
**Colors**: Full color primary, with white backup for dark backgrounds

**Prohibited**
- Never distort, rotate, or apply effects to logo
- Never change colors (brand blue only)
- Never place on competing backgrounds
- Never use without clear space

## Document Standards

### PowerPoint Presentations

**Slide Templates**
1. Title Slide: Logo, title, date, presenter name
2. Section Divider: Section title on blue background
3. Content Slide: Navy title bar, white content area
4. Data Slide: Charts using brand colors, proper legends

**Layout Requirements**
- Margins: 0.5 inches all sides
- Title position: Top 15% of slide
- Bullet indentation: 0.25 inches per level (max 6 bullets)
- Line spacing: 1.15x for readability
- Charts: Brand blue primary series, green secondary

**Accessibility**
- Avoid pure red/green combinations (colorblind friendly)
- Maintain 4.5:1 text contrast minimum
- Use sans-serif fonts only
- Alt text for all images and charts

### Excel Spreadsheets

**Formatting Standards**
- Headers: Row 1, Bold, White on Acme Blue background
- Subheaders: Bold, Acme Navy text
- Data cells: Regular, Acme Navy text
- Borders: Thin, Neutral Gray (#6C757D)
- Alternating rows: Light Gray (#F8F9FA) for readability

**Number Formatting**
- Thousands separator: comma (1,234)
- Currency: $X,XXX.XX
- Percentages: XX.X% (one decimal)
- Dates: Month DD, YYYY format

**Charts**
- Primary series: Acme Blue
- Secondary series: Success Green
- Gridlines: Neutral Gray, 0.5pt
- No 3D effects or complex gradients

### PDF Documents

**Page Layout**
- Header: Logo left (0.5 inch), title center, page number right
- Footer: Copyright left, date center, classification right
- Body margins: 1 inch all sides
- Line spacing: 1.15
- Paragraph spacing: 12pt after

**Section Formatting**
- Main headings: Acme Blue, 16pt, bold
- Subheadings: Acme Navy, 14pt, semibold
- Body text: Acme Navy, 11pt, regular
- Captions: Neutral Gray, 9pt, italic

**Tables in PDFs**
- Header row: Acme Blue background, white text
- Alternating row colors: None or light gray
- Borders: Thin, Neutral Gray
- Number alignment: Right-aligned

## Content Guidelines

### Tone of Voice

- **Professional**: Formal but approachable
- **Clear**: Avoid jargon, use simple language
- **Active**: Use active voice, action-oriented
- **Positive**: Focus on solutions and benefits
- **Inclusive**: Use inclusive language, accessible language

### Standard Phrases

**Opening Statements**
- "At Acme Corporation, we..."
- "Our commitment to innovation..."
- "Delivering excellence through..."

**Closing Statements**
- "Thank you for your continued partnership."
- "We look forward to serving your needs."
- "Together, we achieve excellence."

**Data Presentation**
- Use "significant" not "huge"
- Use "achieved" not "crushed"  
- Use precise numbers, not rounded estimates
- Include context and comparisons

### Prohibited Content

- No clip art or unapproved stock photos
- No Comic Sans, Papyrus, or decorative fonts
- No rainbow or neon colors
- No mentions of competitors by name
- No unverified claims or statistics

## Quality Standards

**Before Publishing**

Checklist:
- Logo properly placed and sized
- All colors match brand palette exactly
- Fonts consistent throughout document
- No typos or grammatical errors
- Data accurately presented
- Professional tone maintained
- Accessibility requirements met
- Legal/compliance reviewed if needed

**Common Issues**

| Issue | Resolution |
|-------|-----------|
| Wrong blue color | Use #0066CC RGB(0,102,204) |
| Distorted logo | Resize proportionally, don't distort |
| Inconsistent fonts | Use only Segoe UI or system-ui |
| Poor contrast | Ensure 4.5:1 ratio for text |

## Application Process

When creating documents:
1. Start with correct brand colors and fonts
2. Apply appropriate template/structure
3. Include logo on first page/slide
4. Format all content consistently
5. Review against this guide
6. Run compliance check

## Automation

**Scripts Included**
- `apply_brand.py` - Automatically applies brand formatting
- `validate_brand.py` - Validates document brand compliance
- `brand_checker.py` - Quick compliance verification

**Integration**
- Integrates with office automation APIs
- Batch processing for multiple documents
- Generates compliance reports

## Governance

**Document Review**
- External communications: Legal review required
- Internal documents: Manager approval
- Sensitive topics: Compliance team review

**Updates**
- Brand guidelines reviewed quarterly
- Changes communicated 30 days in advance
- Version history maintained
- Legacy documents updated on revision

## Exceptions & Appeals

Special projects may request exceptions (e.g., third-party co-branding). Submit requests to:
- Marketing Director for visual exceptions
- Legal for messaging exceptions
- CTO for technical documentation variations

## Contact & Support

- Brand Standards Owner: Marketing@acmecorp.com
- Design Questions: Design@acmecorp.com
- Compliance Issues: Compliance@acmecorp.com

---

**Version**: 2.1  
**Last Updated**: 2025-03-05  
**Next Review**: 2025-06-05  
**Status**: Active and Enforced
