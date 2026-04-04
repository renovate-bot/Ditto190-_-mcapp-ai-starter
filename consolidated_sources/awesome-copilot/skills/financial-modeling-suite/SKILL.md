---
name: financial-modeling-suite
description: Advanced financial modeling toolkit providing DCF valuation, sensitivity analysis, Monte Carlo simulation, and scenario planning for investment decisions and risk assessment
license: MIT
compatibility:
  - min-version: '1.0'
    platforms:
      - claude
      - copilot
allowed-tools:
  - read_file
  - write_file
  - code_execution
metadata:
  source: claude-cookbooks
  category: financial-modeling
  domain: finance
  complexity: advanced
  tags:
    - dcf-analysis
    - valuation
    - risk-assessment
    - scenario-planning
    - monte-carlo
  authors:
    - name: Anthropic Team
      github: anthropics
---

# Financial Modeling Suite Skill

Professional-grade financial modeling toolkit for valuation, investment analysis, and risk assessment using industry-standard methodologies.

## Overview

Comprehensive suite for building sophisticated financial models used by investment banks, private equity firms, and institutional investors. Supports DCF analysis, sensitivity testing, Monte Carlo simulation, and scenario planning.

## Core Capabilities

### 1. Discounted Cash Flow (DCF) Analysis

Build complete valuation models with:
- Multi-stage growth scenarios (explicit forecast period + terminal value)
- Free Cash Flow projections from financials
- Weighted Average Cost of Capital (WACC) calculation
- Terminal value using perpetuity growth or exit multiples
- Enterprise and Equity Value calculations
- Sensitivity to key assumptions

**Supported Models**
- Stable growth companies
- High-growth startups (J-curve projections)
- Mature businesses with decline scenarios
- Turnaround situations

### 2. Sensitivity Analysis

Identify key value drivers:
- Test individual variable impacts
- Multi-variable sensitivity tables
- Tornado charts ranking assumption importance
- Break-even analysis identifying critical thresholds
- Scenario comparison matrices

**Analysis Types**
- One-way sensitivity (single variable)
- Two-way tables (paired variables)
- Data tables for presentations
- Spider diagrams for driver ranking

### 3. Monte Carlo Simulation

Model uncertainty and risk:
- Probability distributions for uncertain variables
- Correlation matrices between assumptions
- Thousands of iterations generating outcome distributions
- Confidence intervals (90%, 95%, 99%)
- Risk metrics (Value-at-Risk, probability of loss)
- Output visualization with histograms

**Distribution Support**
- Normal/Gaussian
- Lognormal
- Triangular
- Uniform
- Custom distributions

### 4. Scenario Planning

Compare strategic alternatives:
- Best/Base/Worst case scenarios
- Multiple economic environment models
- Strategic initiative impact assessment
- Probability-weighted expected values
- Decision tree analysis

**Scenario Types**
- Downside/Base/Upside recession models
- Product launch success/failure scenarios
- M&A transaction structures
- Capital allocation alternatives

## Input Requirements

### DCF Analysis

**Historical Data** (3-5 years)
- Revenue and growth rates
- Operating margins (EBITDA, EBIT, Net margins)
- Tax rates
- Capital expenditures
- Working capital requirements

**Forward Assumptions**
- Revenue growth rates (explicit period)
- Operating margin progression
- Capex as % of revenue
- Working capital changes
- Terminal growth rate or exit multiple
- Risk-free rate, beta, market risk premium

### Sensitivity & Scenario

- Base case model and output metric
- Variables to test and their ranges
- Correlation assumptions if testing multiple factors

### Monte Carlo

- Probability distributions for each uncertain variable
- Correlation matrix between variables
- Number of iterations (1,000-10,000+)
- Random seed for reproducibility

## Output Formats

### DCF Model Results
```
Enterprise Value: $500M
Equity Value: $450M
Implied P/E: 15.2x
Valuation Range: $400M - $600M (±20%)
Sensitivity to WACC: ±$50M per 1% change
```

### Sensitivity Output
- Data tables showing value ranges
- Tornado chart showing driver importance
- Break-even values for key assumptions
- Graphical visualization of relationships

### Monte Carlo Output
- Probability distribution graph
- Statistical summary (mean, median, standard deviation)
- Confidence intervals
- Risk metrics and percentiles
- Histogram with probability bands

### Scenario Comparison
- Side-by-side scenario analysis
- Probability-weighted outcomes
- Decision tree visualization
- Variance analysis vs base case

## Supported Model Types

**Corporate Valuation**
- Mature technology companies
- Growth-stage SaaS companies
- Traditional manufacturing
- Financial services companies

**Project Finance**
- Infrastructure projects
- Real estate developments
- Energy and renewables
- Transportation projects

**Merger & Acquisition**
- Acquisition valuations
- Synergy modeling
- Accretion/dilution analysis
- Merger premium analysis

**Leveraged Buyout (LBO)**
- Acquisition financing analysis
- Returns analysis (IRR, Multiple on Invested Capital)
- Debt capacity assessment
- Exit scenario analysis

## Best Practices Implemented

**Model Design**
- Separation of assumptions, calculations, outputs
- Consistent formatting and structure
- Error checking and data validation
- Clear documentation of formulas
- Version control integration

**Financial Theory**
- CAPM for cost of equity
- WACC calculation
- Terminal value methods
- Comparable company multiples
- Implied multiples from DCF

**Risk Management**
- Sensitivity analysis for key risks
- Monte Carlo for uncertainty quantification
- Stress testing extreme scenarios
- Correlation analysis between variables
- Confidence intervals for valuation ranges

## Quality Standards

Automatic validation includes:
- Income statement balancing checks
- Cash flow reconciliation (CFO = Net Income + Changes)
- Terminal value reasonableness (3-5% growth range)
- WACC validation (reasonable risk/return)
- Circular reference resolution
- Outlier detection in distributions

## Technology

**Scripts Included**
- `dcf_model.py` - Complete DCF valuation engine
- `sensitivity_analysis.py` - Sensitivity testing and analysis
- `monte_carlo.py` - Probability distribution modeling

**Computational Requirements**
- Python 3.12+ with numpy, scipy
- Supports large-scale simulations (10K+ iterations)
- Optimized for performance

## Limitations & Disclaimers

- Models are only as good as their assumptions
- No guarantee of future performance
- Does not include qualitative factors (management, strategy, competitive position)
- Tax implications may be jurisdiction-specific
- Market conditions can change rapidly
- Regulatory and accounting changes may impact results
- **Not a substitute for professional financial or investment advice**

## Use Cases

**Investment Banking**
- M&A fairness opinions
- Valuation for deal structuring
- Pitch book analysis

**Private Equity**
- Investment underwriting
- LBO economics
- Return projections

**Corporate Finance**
- Strategic investment evaluation
- Acquisition assessment
- Divested business valuation

**Equity Research**
- Target price development
- Valuation support
- Sensitivity frameworks

---

**Version**: 1.0  
**Last Updated**: 2025-03-05  
**Status**: Production Ready  
**Maintenance**: Quarterly updates for factor defaults
