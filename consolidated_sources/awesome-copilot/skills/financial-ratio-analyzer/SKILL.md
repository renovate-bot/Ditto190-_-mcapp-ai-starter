---
name: financial-ratio-analyzer
description: Analyzes key financial ratios and metrics from financial statements for comprehensive investment analysis and company performance evaluation
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
  category: financial-analysis
  domain: finance
  tags:
    - financial-analysis
    - ratios
    - investment
    - valuation
  authors:
    - name: Anthropic Team
      github: anthropics
---

# Financial Ratio Analyzer Skill

Comprehensive financial ratio analysis for evaluating company performance, profitability, liquidity, leverage, efficiency, and valuation metrics.

## Overview

This skill provides professional financial ratio analysis equivalent to institutional-grade financial analysis. Calculate and interpret key metrics used by investment professionals, financial analysts, and credit rating agencies.

## Capabilities

**Profitability Analysis**
- Return on Equity (ROE)
- Return on Assets (ROA)
- Gross Margin, Operating Margin, Net Margin
- EBITDA Margin

**Liquidity Assessment**
- Current Ratio
- Quick Ratio
- Cash Ratio
- Working Capital Analysis

**Leverage & Solvency**
- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Debt Service Coverage Ratio
- Long-term Debt Ratio

**Efficiency Metrics**
- Asset Turnover
- Inventory Turnover
- Receivables Turnover
- Days Sales Outstanding (DSO)

**Valuation Metrics**
- Price-to-Earnings (P/E)
- Price-to-Book (P/B)
- Price-to-Sales (P/S)
- EV/EBITDA
- PEG Ratio

**Per-Share Analysis**
- Earnings Per Share (EPS)
- Book Value per Share
- Dividend Per Share
- Free Cash Flow per Share

## Input Formats

The skill accepts financial data in multiple formats:

**Structured Data**
- CSV files with line items labeled
- JSON with hierarchical financial statements
- Excel files (.xlsx) with organized sections

**Text Input**
- Natural language descriptions of financials
- Financial statement excerpts
- Quarterly/annual report data

**Specific Requirements**
- Income Statement: Revenue, COGS, Operating Expenses, Interest, Taxes, Net Income
- Balance Sheet: Assets (current and non-current), Liabilities (current and long-term), Equity
- Cash Flow: Operating, Investing, Financing activities

## Output Formats

Results provided in multiple formats:

**Detailed Report**
- Calculated ratios with values
- Industry benchmark comparisons
- Multi-period trend analysis
- Strengths and weaknesses assessment
- Investment implications

**Professional Formats**
- PDF report with charts
- Excel workbook with formatted tables
- Dashboard-ready JSON
- HTML report for sharing

## Usage Examples

**Basic Analysis**
"Calculate all key financial ratios for this company based on last year's 10-K filing."

**Comparative Analysis**
"Compare the profitability ratios of Company A vs Company B from these financial statements."

**Trend Analysis**
"Analyze the 5-year trend in liquidity ratios - what's the trajectory?"

**Investment Decision Support**
"Based on these financials, is this company undervalued at the current PE ratio of 12x?"

**Credit Analysis**
"Assess the solvency and debt service capability of this company."

## Process

1. **Data Validation**: Verify financial data completeness and consistency
2. **Calculation**: Compute all relevant ratios from provided data
3. **Benchmarking**: Compare against industry averages and peers
4. **Interpretation**: Provide context-specific analysis and insights
5. **Visualization**: Generate charts and summaries for decision support

## Best Practices

- Always validate data completeness before analysis
- Use multiple years for trend identification (minimum 2-3 years)
- Consider industry context - ratios vary significantly by sector
- Cross-check calculations using alternative methods
- Flag unusual values and investigate causes
- Use peer comparison for context
- Consider business cycle impacts

## Limitations

- Requires accurate, timely financial data
- Industry benchmarks are general guidelines only
- Historical performance doesn't predict future results
- Doesn't account for qualitative factors (management, strategy, market position)
- Some ratios may not apply to all industries
- Does not provide investment recommendations
- Professional judgment required for final decisions

## Technology

**Scripts Included**
- `calculate_ratios.py` - Comprehensive ratio calculation engine
- `interpret_ratios.py` - Interpretation framework with benchmarking

**Dependencies**
- Python 3.12+
- pandas, numpy for calculations
- matplotlib for visualizations

## Quality Assurance

The skill implements comprehensive validation:
- Data consistency checks
- Circular reference detection
- Outlier flagging
- Peer comparison validation
- Ratio cross-verification

## Examples & Templates

Reference examples provided for:
- Balance sheet analysis
- Income statement interpretation
- Cash flow assessment
- Multi-company comparisons
- Industry trend analysis

---

**Version**: 1.0  
**Last Updated**: 2025-03-05  
**Status**: Production Ready
