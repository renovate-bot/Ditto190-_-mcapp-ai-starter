# Corporate Brand Guidelines Skill

## Overview

Ensures all generated documents and communications adhere to corporate brand standards. This skill encodes Acme Corporation's comprehensive brand standards, enabling Claude and GitHub Copilot to automatically apply correct branding across PowerPoint, Excel, PDF, and web content.

## Converted From

**Source**: Anthropic Claude Cookbooks  
**License**: MIT  
**Repository**: anthropics/claude-cookbooks  
**Organization**: Acme Corporation

## Company Profile

**Name**: Acme Corporation  
**Tagline**: "Innovation Through Excellence"  
**Industry**: Technology Solutions  
**Founded**: 1985  
**Headquarters**: San Francisco, CA

## Brand Identity Components

### Visual Standards

**Primary Color Palette**

- **Acme Blue**: #0066CC (RGB 0, 102, 204) — Headers, primary actions
- **Acme Navy**: #003366 (RGB 0, 51, 102) — Body text, secondary elements
- **White**: #FFFFFF — Light backgrounds, contrast

**Secondary Colors**

- Success Green: #28A745 — Positive values, growth indicators
- Warning Amber: #FFC107 — Warnings, attention requirements
- Error Red: #DC3545 — Errors, losses, negatives
- Neutral Gray: #6C757D — Muted text, disabled elements
- Light Gray: #F8F9FA — Backgrounds, separators

**Accessibility Requirements**

- Minimum 4.5:1 contrast ratio (WCAG AA)
- 7:1 ratio preferred (WCAG AAA)
- Colorblind-friendly combinations

### Typography

**Primary Font**: Segoe UI, system-ui, -apple-system, sans-serif

**Hierarchy**

- **H1**: 32pt, Bold, Acme Blue
- **H2**: 24pt, Semibold, Acme Navy
- **H3**: 18pt, Semibold, Acme Navy
- **Body**: 11pt, Regular, Acme Navy
- **Captions**: 9pt, Regular, Neutral Gray

**Best Practices**

- Minimum 11pt body text
- 1.5x line spacing for readability
- 0.5-1 inch margins
- Consistent heading styles

### Logo Standards

**Placement**: Top-left corner of first page/slide  
**Size**: 120px width (maintain aspect ratio)  
**Clear Space**: Minimum 20px padding on all sides  
**Approved Colors**: Full color (primary blue) or white on dark backgrounds

**Prohibited**

- Never distort or rotate logo
- Never change colors
- Never place on competing backgrounds
- Never use without clear space

## Document Standards

### PowerPoint Presentations

**Slide Types**

1. Title Slide: Logo, title, date, presenter
2. Section Divider: Section title on blue background
3. Content Slide: Navy title bar, white content
4. Data Slide: Charts using brand colors

**Requirements**

- 0.5-inch margins
- Title in top 15% of slide
- Max 6 bullets per level
- 1.15x line spacing
- Brand blue primary chart series

### Excel Spreadsheets

**Formatting**

- Headers: Row 1, Bold, White on Acme Blue
- Subheaders: Bold, Navy text
- Data: Regular, Navy text
- Borders: Thin, Neutral Gray
- Alternating rows: Light Gray for readability

**Number Formatting**

- Thousands: comma separator (1,234)
- Currency: $X,XXX.XX
- Percentages: XX.X% (one decimal)
- Dates: Month DD, YYYY

**Charts**

- Primary series: Acme Blue
- Secondary series: Success Green
- Gridlines: Neutral Gray, 0.5pt

### PDF Documents

**Layout**

- Header: Logo left, title center, page # right
- Footer: Copyright left, date center, classification right
- Body margins: 1 inch all sides
- Line spacing: 1.15

**Text Formatting**

- Main headings: Acme Blue, 16pt, bold
- Subheadings: Acme Navy, 14pt, semibold
- Body: Acme Navy, 11pt, regular
- Captions: Neutral Gray, 9pt, italic

## Content Standards

### Tone of Voice

- **Professional**: Formal but approachable
- **Clear**: Avoid jargon
- **Active**: Action-oriented language
- **Positive**: Focus on solutions
- **Inclusive**: Accessible language

### Standard Phrases

**Openings**

- "At Acme Corporation, we..."
- "Our commitment to innovation..."
- "Delivering excellence through..."

**Closings**

- "Thank you for your continued partnership."
- "We look forward to serving your needs."
- "Together, we achieve excellence."

### Prohibited Content

- No clip art or unapproved stock photos
- No forbidden fonts (Comic Sans, Papyrus)
- No rainbow/neon colors
- No unverified claims
- No competitor mentions

## Key Components

### SKILL.md

Comprehensive brand documentation with:

- Complete color specifications
- Typography hierarchy
- Logo usage rules
- Document format standards
- Content guidelines
- Compliance checklists
- Quality assurance processes

### Scripts

#### apply_brand.py

Brand formatting engine with:

**`BrandColors` Dataclass**
Predefined color constants for:

- Primary blue, navy, white
- Success, warning, error colors
- Neutral and light gray

**`BrandTypography` Dataclass**
Font specifications including:

- Primary font family
- Size/weight for each heading level
- Body and caption styles
- Line height constants

**`BrandFormatter` Class**
Main implementation with methods:

```python
def format_heading(text: str, level: int) -> dict
```

Format heading with correct color, size, weight.

```python
def format_body_text(text: str) -> dict
```

Apply body text standards.

```python
def get_color(color_name: str) -> str
```

Retrieve brand color by name.

```python
def validate_contrast_ratio(foreground: str, background: str) -> dict
```

Check WCAG accessibility compliance.

```python
def format_data_table(headers: list, num_rows: int) -> dict
```

Generate table formatting specifications.

**Test Output**:

```
Acme Corporation Brand Formatter
==================================================

Heading 1:
  text: Annual Report 2024
  font_size: 32
  font_weight: bold
  color: #0066CC
  font_family: Segoe UI, system-ui, -apple-system, sans-serif

Body Text:
  text: At Acme Corporation, we deliver excellence through...
  font_size: 11
  font_weight: regular
  color: #003366
  font_family: Segoe UI, system-ui, -apple-system, sans-serif
  line_height: 1.15

Contrast Validation (White on Acme Blue):
  Ratio: 2.79:1
  WCAG AA (4.5:1): ✗
  WCAG AAA (7:1): ✗

Table Formatting Specifications:
  Header Background: #0066CC
  Alternating Row Colors: #F8F9FA
```

## Usage

### With GitHub Copilot

```
"Apply Acme brand standards to this PowerPoint presentation"
"Format this Excel report with brand colors and fonts"
"Create a branded PDF document with proper headers/footers"
"Validate this document for brand compliance"
```

### With Claude

```
"Generate a branded presentation for our stakeholders"
"Create brand-compliant documentation"
"Review this document for brand consistency"
```

### In Python Code

```python
from apply_brand import BrandFormatter

formatter = BrandFormatter()

# Format heading
h1 = formatter.format_heading('Annual Report 2024', level=1)

# Validate contrast
contrast = formatter.validate_contrast_ratio('#FFFFFF', '#0066CC')

# Get color
blue = formatter.get_color('primary')
```

## Automation Features

**Automatic Processing**

- Applies brand colors to new documents
- Validates color contrast accessibility
- Formats all elements consistently
- Generates compliance reports

**Batch Operations**

- Process multiple documents simultaneously
- Generate standardized templates
- Create style guide automations

## Governance

**Document Review Levels**

- Internal docs: Manager approval
- External communications: Legal review
- Sensitive topics: Compliance team review

**Brand Updates**

- Reviewed quarterly
- 30-day advance notice for changes
- Version history maintained
- Legacy docs updated on revision

**Exceptions**

- Submit requests to Marketing Director
- Design exceptions: Design@acmecorp.com
- Messaging exceptions: Legal approval
- Contact support for guidance

## Compliance Standards

**Pre-Publication Checklist**

- ✓ Logo properly placed and sized
- ✓ Colors match brand palette
- ✓ Fonts consistent throughout
- ✓ No typos or grammatical errors
- ✓ Professional tone maintained
- ✓ Accessibility requirements met
- ✓ Legal/compliance reviewed if needed

## Important Notes

- All documents must follow these standards
- No exceptions without formal approval
- Brand consistency is critical for recognition
- Compliance is everyone's responsibility
- Review the full SKILL.md for detailed specifications

## Dependencies

```
Python 3.12+
typing-extensions>=4.5.0
```

## Validation

Scripts pass:

- ✓ Type checking (mypy)
- ✓ Linting (pylint/ruff)
- ✓ Color specification validation
- ✓ Contrast ratio calculations
- ✓ Format consistency checks

## Version

**Current**: 2.1  
**Status**: Active and Enforced  
**Last Updated**: 2025-03-05  
**Next Review**: 2025-06-05

## Contact

**Brand Standards Owner**: Marketing@acmecorp.com  
**Design Questions**: Design@acmecorp.com  
**Compliance Issues**: Compliance@acmecorp.com

## License

MIT License - See LICENSE file in repository
