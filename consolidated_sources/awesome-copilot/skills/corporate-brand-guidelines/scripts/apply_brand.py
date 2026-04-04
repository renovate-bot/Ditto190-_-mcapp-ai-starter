#!/usr/bin/env python3
"""
Brand Formatter - Apply Acme Corporation brand standards

Converts Claude Skills brand application capability to GitHub Copilot AgentSkills format.
Applies corporate brand standards to documents.

PEP 723 dependencies:
    dataclasses>=0.6
    typing-extensions>=4.5.0
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class BrandColors:
    """Acme Corporation brand colors."""
    
    primary_blue: str = '#0066CC'      # RGB(0, 102, 204)
    navy: str = '#003366'              # RGB(0, 51, 102)
    white: str = '#FFFFFF'
    success_green: str = '#28A745'
    warning_amber: str = '#FFC107'
    error_red: str = '#DC3545'
    neutral_gray: str = '#6C757D'
    light_gray: str = '#F8F9FA'


@dataclass
class BrandTypography:
    """Acme Corporation typography standards."""
    
    primary_font: str = 'Segoe UI, system-ui, -apple-system, sans-serif'
    heading_1_size: int = 32
    heading_2_size: int = 24
    heading_3_size: int = 18
    body_size: int = 11
    caption_size: int = 9
    line_height: float = 1.15


class BrandFormatter:
    """Apply Acme Corporation brand standards to documents."""
    
    def __init__(self):
        self.colors = BrandColors()
        self.typography = BrandTypography()
        self.company_name = 'Acme Corporation'
        self.tagline = 'Innovation Through Excellence'
    
    def format_heading(
        self,
        text: str,
        level: Literal[1, 2, 3] = 1,
    ) -> dict[str, str | int]:
        """Format heading with brand standards.
        
        Args:
            text: Heading text
            level: Heading level (1, 2, or 3)
            
        Returns:
            Dict with formatted heading properties
        """
        if level == 1:
            return {
                'text': text,
                'font_size': self.typography.heading_1_size,
                'font_weight': 'bold',
                'color': self.colors.primary_blue,
                'font_family': self.typography.primary_font,
            }
        elif level == 2:
            return {
                'text': text,
                'font_size': self.typography.heading_2_size,
                'font_weight': 'semibold',
                'color': self.colors.navy,
                'font_family': self.typography.primary_font,
            }
        else:  # level == 3
            return {
                'text': text,
                'font_size': self.typography.heading_3_size,
                'font_weight': 'semibold',
                'color': self.colors.navy,
                'font_family': self.typography.primary_font,
            }
    
    def format_body_text(self, text: str) -> dict[str, str | int | float]:
        """
        Format body text with brand standards.
        
        Args:
            text: Body text content
            
        Returns:
            Dict with formatted text properties
        """
        return {
            'text': text,
            'font_size': self.typography.body_size,
            'font_weight': 'regular',
            'color': self.colors.navy,
            'font_family': self.typography.primary_font,
            'line_height': self.typography.line_height,
        }
    
    def get_color(self, color_name: str) -> str:
        """
        Get brand color by name.
        
        Args:
            color_name: Name of the color
            
        Returns:
            Color hex code
            
        Raises:
            ValueError: If color name not recognized
        """
        color_map = {
            'primary': self.colors.primary_blue,
            'navy': self.colors.navy,
            'white': self.colors.white,
            'success': self.colors.success_green,
            'warning': self.colors.warning_amber,
            'error': self.colors.error_red,
            'gray': self.colors.neutral_gray,
            'light_gray': self.colors.light_gray,
        }
        
        if color_name not in color_map:
            raise ValueError(
                f"Color '{color_name}' not found. "
                f"Available: {', '.join(color_map.keys())}"
            )
        
        return color_map[color_name]
    
    def validate_contrast_ratio(
        self,
        foreground: str,
        background: str,
    ) -> dict[str, float | bool]:
        """
        Validate color contrast ratio for accessibility.
        
        Args:
            foreground: Foreground color hex code
            background: Background color hex code
            
        Returns:
            Dict with contrast ratio and WCAG compliance
        """
        # Simplified contrast calculation
        # In production, use full WCAG contrast formula
        
        # Parse hex colors to RGB
        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))  # type: ignore
        
        fg_rgb = hex_to_rgb(foreground)
        bg_rgb = hex_to_rgb(background)
        
        # Calculate relative luminance
        def luminance(rgb: tuple[int, int, int]) -> float:
            return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        l1 = luminance(fg_rgb)
        l2 = luminance(bg_rgb)
        
        # Contrast ratio
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        
        return {
            'ratio': round(ratio, 2),
            'wcag_aa': ratio >= 4.5,  # Minimum for normal text
            'wcag_aaa': ratio >= 7.0,  # Enhanced for normal text
        }
    
    def format_data_table(
        self,
        headers: list[str],
        num_rows: int,
    ) -> dict[str, dict | list]:
        """
        Format data table with brand standards.
        
        Args:
            headers: Table column headers
            num_rows: Number of data rows
            
        Returns:
            Dict with table formatting specifications
        """
        return {
            'header': {
                'background_color': self.colors.primary_blue,
                'text_color': self.colors.white,
                'font_weight': 'bold',
                'font_size': 11,
            },
            'data_rows': {
                'odd_background': self.colors.white,
                'even_background': self.colors.light_gray,
                'text_color': self.colors.navy,
                'font_size': 11,
            },
            'borders': {
                'color': self.colors.neutral_gray,
                'width': 0.5,
            },
            'alignment': {
                'headers': 'left',
                'numbers': 'right',
                'text': 'left',
            },
        }


def main() -> None:
    """Demonstrate brand formatting."""
    
    formatter = BrandFormatter()
    
    print("Acme Corporation Brand Formatter")
    print("=" * 50)
    
    # Format heading
    h1 = formatter.format_heading('Annual Report 2024', level=1)
    print("\nHeading 1:")
    for key, value in h1.items():
        if key == 'text':
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    
    # Format body text
    body = formatter.format_body_text(
        'At Acme Corporation, we deliver excellence through innovation.'
    )
    print("\nBody Text:")
    for key, value in body.items():
        if key == 'text':
            val_str = str(value)
            print(f"  {key}: {val_str[:50]}...")
        else:
            print(f"  {key}: {value}")
    
    # Validate contrast
    contrast = formatter.validate_contrast_ratio(
        formatter.colors.white,  # Text color
        formatter.colors.primary_blue,  # Background color
    )
    print("\nContrast Validation (White on Acme Blue):")
    print(f"  Ratio: {contrast['ratio']}:1")
    print(f"  WCAG AA (4.5:1): {'✓' if contrast['wcag_aa'] else '✗'}")
    print(f"  WCAG AAA (7:1): {'✓' if contrast['wcag_aaa'] else '✗'}")
    
    # Table formatting
    table = formatter.format_data_table(
        headers=['Product', 'Revenue', 'Growth'],
        num_rows=5,
    )
    print("\nTable Formatting Specifications:")
    header_info = table.get('header')
    if isinstance(header_info, dict):
        bg_color = header_info.get('background_color')
        print(f"  Header Background: {bg_color}")
    
    data_info = table.get('data_rows')
    if isinstance(data_info, dict):
        even_bg = data_info.get('even_background')
        print(f"  Alternating Row Colors: {even_bg}")


if __name__ == '__main__':
    main()
