#!/usr/bin/env python3
"""
DCF Valuation Model

Converts Claude Skills financial modeling capability to GitHub Copilot AgentSkills format.
Builds comprehensive discounted cash flow models for enterprise valuation.

PEP 723 dependencies:
    dataclasses>=0.6
    typing-extensions>=4.5.0
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple


class DCFAssumptions(NamedTuple):
    """DCF model assumptions."""
    revenue_growth: list[float]
    ebitda_margin: list[float]
    tax_rate: float
    capex_pct_revenue: float
    nwc_pct_revenue: float
    wacc: float
    terminal_growth: float


@dataclass
class DCFResults:
    """DCF valuation results."""
    fcf_projections: list[float]
    terminal_value: float
    pv_fcf: float
    pv_terminal: float
    enterprise_value: float
    equity_value: float | None = None


def build_dcf_model(
    current_revenue: float,
    assumptions: DCFAssumptions,
    forecast_years: int = 5,
) -> DCFResults:
    """
    Build a complete DCF valuation model.
    
    Args:
        current_revenue: Latest annual revenue
        assumptions: DCF assumptions
        forecast_years: Explicit forecast period years
        
    Returns:
        DCFResults with valuations
    """
    
    # Project revenues
    revenues = [current_revenue]
    for i in range(forecast_years):
        revenues.append(revenues[-1] * (1 + assumptions.revenue_growth[i]))
    
    # Project EBITDA and tax rates
    ebitda = [
        revenues[i + 1] * assumptions.ebitda_margin[i] for i in range(forecast_years)
    ]
    
    # Calculate Free Cash Flows
    # FCF = EBIT(1-Tax Rate) + DA - CapEx - Change in NWC
    fcf = []
    for i in range(forecast_years):
        # Simplified FCF = EBITDA * (1 - tax) - CapEx - NWC change
        fcf_simple = (
            ebitda[i] * (1 - assumptions.tax_rate) -
            revenues[i + 1] * assumptions.capex_pct_revenue -
            revenues[i + 1] * assumptions.nwc_pct_revenue * 0.1  # 10% change
        )
        fcf.append(fcf_simple)
    
    # Calculate terminal value using perpetuity growth
    terminal_fcf = fcf[-1] * (1 + assumptions.terminal_growth)
    terminal_value = terminal_fcf / (assumptions.wacc - assumptions.terminal_growth)
    
    # Discount to present value
    pv_fcf = sum(
        fcf[i] / ((1 + assumptions.wacc) ** (i + 1))
        for i in range(forecast_years)
    )
    pv_terminal = terminal_value / ((1 + assumptions.wacc) ** forecast_years)
    
    enterprise_value = pv_fcf + pv_terminal
    
    return DCFResults(
        fcf_projections=fcf,
        terminal_value=terminal_value,
        pv_fcf=pv_fcf,
        pv_terminal=pv_terminal,
        enterprise_value=enterprise_value,
    )


def calculate_wacc(
    risk_free_rate: float,
    market_risk_premium: float,
    beta: float,
    after_tax_cost_of_debt: float,
    market_cap: float,
    debt: float,
) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).
    
    Args:
        risk_free_rate: Risk-free rate (e.g., 10-year Treasury)
        market_risk_premium: Expected market risk premium
        beta: Company beta coefficient
        after_tax_cost_of_debt: Cost of debt after tax effect
        market_cap: Current market capitalization
        debt: Total debt outstanding
        
    Returns:
        WACC as a decimal (e.g., 0.08 for 8%)
    """
    
    total_value = market_cap + debt
    
    # Cost of equity using CAPM
    cost_of_equity = risk_free_rate + beta * market_risk_premium
    
    # WACC
    wacc = (
        (market_cap / total_value) * cost_of_equity +
        (debt / total_value) * after_tax_cost_of_debt
    )
    
    return wacc


def main() -> None:
    """Demonstrate DCF model building."""
    
    assumptions = DCFAssumptions(
        revenue_growth=[0.10, 0.08, 0.06, 0.04, 0.03],  # 10%, 8%, 6%, 4%, 3%
        ebitda_margin=[0.30, 0.32, 0.33, 0.33, 0.33],  # 30-33% EBITDA margins
        tax_rate=0.21,  # 21% tax rate
        capex_pct_revenue=0.04,  # CapEx = 4% of revenue
        nwc_pct_revenue=0.10,  # NWC = 10% of revenue
        wacc=0.10,  # 10% WACC
        terminal_growth=0.025,  # 2.5% terminal growth
    )
    
    results = build_dcf_model(
        current_revenue=100_000_000,  # $100M revenue
        assumptions=assumptions,
        forecast_years=5,
    )
    
    print("DCF Valuation Results")
    print("=" * 50)
    print(f"\nFree Cash Flow Projections (Years 1-5):")
    for i, fcf in enumerate(results.fcf_projections, 1):
        print(f"  Year {i}: ${fcf:,.0f}")
    
    print(f"\nValuation Summary:")
    print(f"  PV of Explicit Period FCF:  ${results.pv_fcf:,.0f}")
    print(f"  Terminal Value:              ${results.terminal_value:,.0f}")
    print(f"  PV of Terminal Value:        ${results.pv_terminal:,.0f}")
    print(f"  Enterprise Value:            ${results.enterprise_value:,.0f}")
    
    # WACC calculation example
    wacc = calculate_wacc(
        risk_free_rate=0.045,  # 4.5%
        market_risk_premium=0.065,  # 6.5%
        beta=1.2,
        after_tax_cost_of_debt=0.04,  # 4%
        market_cap=500_000_000,  # $500M market cap
        debt=200_000_000,  # $200M debt
    )
    print(f"\nWACC Calculation Example: {wacc:.2%}")


if __name__ == '__main__':
    main()
