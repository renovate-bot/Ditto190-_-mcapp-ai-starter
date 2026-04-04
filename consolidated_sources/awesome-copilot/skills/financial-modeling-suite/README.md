# Financial Modeling Suite Skill

## Overview

Advanced financial modeling toolkit providing DCF valuation, sensitivity analysis, Monte Carlo simulation, and scenario planning. This skill implements industry-standard methodologies used by investment banks, private equity firms, and institutional investors.

## Converted From

**Source**: Anthropic Claude Cookbooks  
**License**: MIT  
**Repository**: anthropics/claude-cookbooks  
**Complexity**: Advanced

## Core Capabilities

### 1. Discounted Cash Flow (DCF) Analysis

Complete valuation models with:

- Multi-stage growth scenarios
- Free Cash Flow projections
- WACC (Weighted Average Cost of Capital) calculation
- Terminal value using perpetuity growth or exit multiples
- Enterprise and Equity value calculations
- Sensitivity analysis on key assumptions

**Supported Model Types**

- Stable growth companies
- High-growth startups (J-curve projections)
- Mature businesses with decline scenarios
- Turnaround situations with recovery patterns

### 2. Sensitivity Analysis

Identify key value drivers:

- One-way variable sensitivity
- Multi-variable sensitivity tables
- Tornado charts ranking driver importance
- Break-even analysis
- Scenario comparison matrices

### 3. Monte Carlo Simulation

Model uncertainty and risk:

- Probability distributions for uncertain variables
- Correlation matrix support
- Thousands of iterations generating outcome distributions
- Confidence intervals (90%, 95%, 99%)
- Risk metrics (Value-at-Risk, probability of loss)

### 4. Scenario Planning

Compare strategic alternatives:

- Best/Base/Worst case scenarios
- Economic environment modeling
- Strategic initiative impact assessment
- Probability-weighted expected values
- Decision tree analysis

## Key Components

### SKILL.md

Comprehensive documentation including:

- Detailed methodology descriptions
- Model type examples
- Input data requirements
- Output format specifications
- Best practices and quality standards
- Use case examples
- Limitations and disclaimers

### Scripts

#### dcf_model.py

Complete DCF valuation engine with:

**`DCFAssumptions` NamedTuple**
Typed container for all DCF assumptions:

- Revenue growth rates (list)
- EBITDA margins (list)
- Tax rate (float)
- Capex as % of revenue (float)
- Net working capital % of revenue (float)
- WACC (float)
- Terminal growth rate (float)

**`DCFResults` Dataclass**
Structured output with:

- FCF projections (list)
- Terminal value (float)
- PV of FCF (float)
- PV of terminal value (float)
- Enterprise value (float)
- Optional equity value (float)

**Key Functions**

```python
def build_dcf_model(
    current_revenue: float,
    assumptions: DCFAssumptions,
    forecast_years: int = 5,
) -> DCFResults
```

Builds complete multi-year DCF model with terminal value.

```python
def calculate_wacc(
    risk_free_rate: float,
    market_risk_premium: float,
    beta: float,
    after_tax_cost_of_debt: float,
    market_cap: float,
    debt: float,
) -> float
```

Calculates Weighted Average Cost of Capital using CAPM.

**Test Output**:

```
DCF Valuation Results
==================================================

Free Cash Flow Projections (Years 1-5):
  Year 1: $20,570,000
  Year 2: $24,092,640
  Year 3: $26,533,030
  Year 4: $27,594,351
  Year 5: $28,422,181

Valuation Summary:
  PV of Explicit Period FCF:  $95,041,182
  Terminal Value:              $388,436,478
  PV of Terminal Value:        $241,188,492
  Enterprise Value:            $336,229,674

WACC Calculation Example: 9.93%
```

## Input Data Requirements

### Historical Data (3-5 years)

- Revenue and growth rates
- Operating margins (EBITDA, EBIT, Net)
- Tax rates
- Capital expenditures (actual or projected % of revenue)
- Working capital requirements

### Forward Assumptions

- Revenue growth rates for explicit forecast period
- Operating margin progression
- Capex as % of revenue
- Working capital changes
- Terminal growth rate (typically 2-3%)
- Risk-free rate, beta, market risk premium

### Optional Data

- Debt levels for WACC calculation
- Market cap for comparables
- Stock price for valuation metrics
- Peer company multiples for validation

## Output Formats

### DCF Model Results

```
Enterprise Value: $500M
Equity Value: $450M
Implied P/E: 15.2x
Valuation Range: $400M - $600M (±20%)
Sensitivity to WACC: ±$50M per 1% change
```

### Sensitivity Analysis Output

- Data tables showing value ranges
- Tornado diagrams showing driver importance
- Break-even values for assumptions
- Graphical relationships

### Scenario Comparison

- Side-by-side scenario analysis
- Probability-weighted outcomes
- Decision trees
- Variance analysis vs base case

### Monte Carlo Output

- Probability distribution graphs
- Statistical summary (mean, median, std dev)
- Confidence intervals
- Risk metrics and percentiles

## Integration Points

### With GitHub Copilot

```
"Build a DCF model for this company"
"What's the sensitivity of valuation to WACC?"
"Compare valuation under bull/base/bear scenarios"
"Calculate intrinsic value using DCF"
```

### With n8n Workflows

- Import financial data from PostgreSQL
- Calculate DCF and scenarios
- Generate valuation reports
- Track assumptions history
- Create comparison analyses

### With Claude

- Complex valuation analysis
- Merger & acquisition pricing
- Private equity transaction modeling
- Startup funding valuations
- Investment thesis development

## Model Quality Standards

Automatically validates:

- Income statement balancing
- Cash flow reconciliation
- Terminal value reasonableness (3-5% growth)
- WACC validation (realistic risk/return)
- Circular reference resolution
- Outlier detection

## Important Notes

**Assumptions Drive Results**

- Valuation highly sensitive to growth and discount rate assumptions
- Use multiple scenarios for conservative/aggressive cases
- Sensitivity analysis critical for understanding drivers

**Not Investment Advice**

- No guarantee of future performance
- Doesn't include qualitative factors (management, competitive position)
- Tax implications may be jurisdiction-specific
- Regulatory changes can significantly impact results

**Professional Context**

- Used by investment bankers for M&A fairness opinions
- Private equity analysis for LBO underwriting
- Corporate finance for strategic investment evaluation
- Equity research for target price development

## Dependencies

```
Python 3.12+
```

No external dependencies required for base functionality.
Optional for advanced features:

- numpy: Numerical optimization
- scipy: Statistical distributions
- pandas: Data manipulation
- matplotlib: Visualization

## Validation

Scripts pass:

- ✓ Type checking (mypy)
- ✓ Linting (pylint/ruff)
- ✓ Mathematical accuracy validation
- ✓ Output format verification
- ✓ Edge case handling

## Version

**Current**: 1.0  
**Status**: Production Ready  
**Last Updated**: 2025-03-05  
**Maintenance**: Quarterly updates for factor defaults

## License

MIT License - See LICENSE file in repository
