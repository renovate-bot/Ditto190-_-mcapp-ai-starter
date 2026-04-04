# Financial Ratio Analyzer Skill

## Overview

Professional financial ratio analysis for evaluating company performance, profitability, liquidity, leverage, efficiency, and valuation metrics. This skill calculates institutional-grade financial ratios used by investment professionals and credit rating agencies.

## Converted From

**Source**: Anthropic Claude Cookbooks  
**License**: MIT  
**Repository**: anthropics/claude-cookbooks

## Capabilities

### Profitability Analysis

- Return on Equity (ROE) and Return on Assets (ROA)
- Gross Margin, Operating Margin, Net Margin
- EBITDA Margin calculations

### Liquidity Assessment

- Current Ratio, Quick Ratio, Cash Ratio
- Working Capital analysis

### Leverage & Solvency

- Debt-to-Equity and Debt-to-Assets ratios
- Interest Coverage Ratio
- Debt Service Coverage

### Efficiency Metrics

- Asset Turnover, Inventory Turnover
- Receivables Turnover
- Days Sales Outstanding (DSO)

### Valuation Metrics

- Price-to-Earnings (P/E), Price-to-Book (P/B)
- Price-to-Sales (P/S)
- EV/EBITDA, PEG Ratio

### Trend Analysis

- Multi-period ratio trends
- Year-over-year comparisons
- Trajectory identification

## Key Components

### SKILL.md

Comprehensive skill documentation including:

- Financial ratio definitions and formulas
- Input format specifications
- Output format options
- Industry-specific considerations
- Best practices and quality standards

### Scripts

#### calculate_ratios.py

Main ratio calculation engine with:

- `FinancialRatios` dataclass for structured results
- `calculate_ratios()` function accepting income statement and balance sheet data
- Support for stock price and historical data for trend analysis
- Handles optional data gracefully

**Usage**:

```python
from calculate_ratios import calculate_ratios

income_stmt = {
    'revenue': 1_000_000,
    'net_income': 200_000,
    'gross_profit': 600_000,
}

balance_sht = {
    'total_assets': 1_500_000,
    'total_equity': 700_000,
}

ratios = calculate_ratios(income_stmt, balance_sht)
print(f"ROA: {ratios.profitability['roa']:.2%}")
```

**Test Output**:

```
Financial Ratios Summary
==================================================

Profitability Ratios:
  roa: 0.1333
  roe: 0.2857
  gross_margin: 0.6000
  operating_margin: 0.3000
  net_margin: 0.2000

Liquidity Ratios:
  current_ratio: 1.5000
  quick_ratio: 0.8333
  cash_ratio: 0.5000

Leverage Ratios:
  debt_to_equity: 0.7143
  interest_coverage: 15.0000
  debt_to_assets: 0.3333

Efficiency Ratios:
  asset_turnover: 0.6667
  inventory_turnover: 2.0000
  receivables_turnover: 10.0000

Valuation Ratios:
  pe_ratio: 15.0000
  pb_ratio: 4.2857
  ps_ratio: 3.0000
```

## Input Formats

### Required Data

**Income Statement**

- Revenue
- Cost of Goods Sold (COGS)
- Gross Profit
- Operating Expenses
- Operating Income
- Interest Expense
- Net Income
- Earnings Per Share (optional)

**Balance Sheet**

- Current Assets (Cash, A/R, Inventory, etc.)
- Total Assets
- Current Liabilities
- Total Debt
- Total Equity
- Accounts Receivable (optional)
- Inventory (optional)
- Shares Outstanding (optional)

### Optional Data

- Stock price (for valuation ratios)
- Prior period financials (for trend analysis)
- Industry benchmarks (for context)

## Output Formats

### Structured Results

Python dataclass with nested dictionaries:

- `profitability`: ROA, ROE, margins
- `liquidity`: Current, Quick, Cash ratios
- `leverage`: Debt ratios, coverage ratios
- `efficiency`: Turnover ratios
- `valuation`: PE, PB, PS ratios
- `trends`: Multi-period trend arrays

### Presentation Formats

- **Ratio Summary**: Calculated values with descriptions
- **Industry Comparison**: Peer benchmarking
- **Trend Report**: Multi-year progression
- **Investment Thesis Support**: Strategic insights

## Integration Points

### With GitHub Copilot

```
"Analyze these Q3 financials and calculate all key ratios"
"Generate a 3-year trend analysis for these companies"
"What's the P/E multiple for this valuation?"
```

### With n8n Workflows

- Read financial data from PostgreSQL
- Calculate ratios in transformation nodes
- Generate analysis reports
- Create comparison tables

### With Claude

- Financial statement analysis
- Investment recommendation support
- Merger & acquisition valuation
- Credit risk assessment

## Important Notes

- **Accuracy**: Ratios are only as good as the input data quality
- **Industry Context**: Ratios vary significantly by sector
- **Use Cases**: Investment analysis, credit assessment, corporate benchmarking
- **Professional Review**: Always validate results with domain experts
- **Not Investment Advice**: Results should inform but not replace professional analysis

## Validation

All scripts pass:

- ✓ Type checking (mypy)
- ✓ Linting (pylint/ruff)
- ✓ Execution validation
- ✓ Output format verification

## Dependencies

```
Python 3.12+
```

No external dependencies required for basic functionality.
Optional for extended features:

- pandas: Data manipulation
- numpy: Numerical calculations
- matplotlib: Visualization

## Version

**Current**: 1.0  
**Status**: Production Ready  
**Last Updated**: 2025-03-05

## Contributing

This skill is maintained as part of the awesome-copilot library. Contributions should:

- Follow the existing code structure
- Include comprehensive docstrings
- Add type hints to all functions
- Update SKILL.md with new features

## License

MIT License - See LICENSE file in repository
