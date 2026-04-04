#!/usr/bin/env python3
"""
Financial Ratio Calculator

Converts Claude Skills financial analysis capability to GitHub Copilot AgentSkills format.
Calculates comprehensive financial ratios from standardized financial data.

PEP 723 dependencies:
    pandas>=2.0.0
    numpy>=1.24.0
    typing-extensions>=4.5.0
"""

from __future__ import annotations
import json
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class FinancialRatios:
    """Container for calculated financial ratios."""
    
    profitability: dict[str, float]
    liquidity: dict[str, float]
    leverage: dict[str, float]
    efficiency: dict[str, float]
    valuation: dict[str, float]
    trends: dict[str, list[float]]


def calculate_ratios(
    income_statement: dict[str, float],
    balance_sheet: dict[str, float],
    stock_price: float | None = None,
    prior_periods: list[dict[str, float]] | None = None,
) -> FinancialRatios:
    """
    Calculate comprehensive financial ratios.
    
    Args:
        income_statement: Income statement items (revenue, expenses, net_income, etc.)
        balance_sheet: Balance sheet items (assets, liabilities, equity, etc.)
        stock_price: Current stock price for valuation ratios
        prior_periods: Prior period data for trend analysis
        
    Returns:
        FinancialRatios object with categorized ratios
    """
    
    # Profitability Ratios
    profitability: dict[str, float] = {}
    if income_statement.get('revenue') and balance_sheet.get('total_assets'):
        profitability['roa'] = (
            income_statement['net_income'] / balance_sheet['total_assets']
        )
    if income_statement.get('net_income') and balance_sheet.get('total_equity'):
        profitability['roe'] = (
            income_statement['net_income'] / balance_sheet['total_equity']
        )
    if income_statement.get('revenue') and income_statement.get('gross_profit'):
        profitability['gross_margin'] = (
            income_statement['gross_profit'] / income_statement['revenue']
        )
    if income_statement.get('revenue') and income_statement.get('operating_income'):
        profitability['operating_margin'] = (
            income_statement['operating_income'] / income_statement['revenue']
        )
    if income_statement.get('revenue') and income_statement.get('net_income'):
        profitability['net_margin'] = (
            income_statement['net_income'] / income_statement['revenue']
        )
    
    # Liquidity Ratios
    liquidity: dict[str, float] = {}
    if balance_sheet.get('current_assets') and balance_sheet.get('current_liabilities'):
        liquidity['current_ratio'] = (
            balance_sheet['current_assets'] / balance_sheet['current_liabilities']
        )
    if (balance_sheet.get('current_assets') and 
        balance_sheet.get('inventory') and 
        balance_sheet.get('current_liabilities')):
        liquidity['quick_ratio'] = (
            (balance_sheet['current_assets'] - balance_sheet['inventory']) /
            balance_sheet['current_liabilities']
        )
    if balance_sheet.get('cash') and balance_sheet.get('current_liabilities'):
        liquidity['cash_ratio'] = (
            balance_sheet['cash'] / balance_sheet['current_liabilities']
        )
    
    # Leverage Ratios
    leverage: dict[str, float] = {}
    if balance_sheet.get('total_debt') and balance_sheet.get('total_equity'):
        leverage['debt_to_equity'] = (
            balance_sheet['total_debt'] / balance_sheet['total_equity']
        )
    if (income_statement.get('operating_income') and 
        income_statement.get('interest_expense') and
        income_statement['interest_expense'] > 0):
        leverage['interest_coverage'] = (
            income_statement['operating_income'] / income_statement['interest_expense']
        )
    if balance_sheet.get('total_debt') and balance_sheet.get('total_assets'):
        leverage['debt_to_assets'] = (
            balance_sheet['total_debt'] / balance_sheet['total_assets']
        )
    
    # Efficiency Ratios
    efficiency: dict[str, float] = {}
    if income_statement.get('revenue') and balance_sheet.get('total_assets'):
        efficiency['asset_turnover'] = (
            income_statement['revenue'] / balance_sheet['total_assets']
        )
    if (income_statement.get('cost_of_goods_sold') and 
        balance_sheet.get('inventory')):
        efficiency['inventory_turnover'] = (
            income_statement['cost_of_goods_sold'] / balance_sheet['inventory']
        )
    if income_statement.get('revenue') and balance_sheet.get('accounts_receivable'):
        efficiency['receivables_turnover'] = (
            income_statement['revenue'] / balance_sheet['accounts_receivable']
        )
    
    # Valuation Ratios
    valuation: dict[str, float] = {}
    if stock_price and income_statement.get('earnings_per_share'):
        valuation['pe_ratio'] = stock_price / income_statement['earnings_per_share']
    if stock_price and balance_sheet.get('book_value_per_share'):
        valuation['pb_ratio'] = stock_price / balance_sheet['book_value_per_share']
    if stock_price and income_statement.get('revenue') and balance_sheet.get('shares_outstanding'):
        valuation['ps_ratio'] = (
            (stock_price * balance_sheet['shares_outstanding']) / 
            income_statement['revenue']
        )
    
    # Trend Analysis
    trends: dict[str, list[float]] = {}
    if prior_periods:
        trends['roe_trend'] = [
            (p['net_income'] / p.get('total_equity', 1)) for p in prior_periods
            if 'net_income' in p and 'total_equity' in p
        ]
        trends['roa_trend'] = [
            (p['net_income'] / p.get('total_assets', 1)) for p in prior_periods
            if 'net_income' in p and 'total_assets' in p
        ]
    
    return FinancialRatios(
        profitability=profitability,
        liquidity=liquidity,
        leverage=leverage,
        efficiency=efficiency,
        valuation=valuation,
        trends=trends,
    )


def main() -> None:
    """Demonstrate financial ratio calculation."""
    
    # Example financial data
    income_stmt = {
        'revenue': 1_000_000,
        'cost_of_goods_sold': 400_000,
        'gross_profit': 600_000,
        'operating_expenses': 300_000,
        'operating_income': 300_000,
        'interest_expense': 20_000,
        'net_income': 200_000,
        'earnings_per_share': 4.0,
    }
    
    balance_sht = {
        'cash': 150_000,
        'accounts_receivable': 100_000,
        'inventory': 200_000,
        'current_assets': 450_000,
        'total_assets': 1_500_000,
        'current_liabilities': 300_000,
        'total_debt': 500_000,
        'total_equity': 700_000,
        'shares_outstanding': 50_000,
        'book_value_per_share': 14.0,
    }
    
    ratios = calculate_ratios(income_stmt, balance_sht, stock_price=60.0)
    
    print("Financial Ratios Summary")
    print("=" * 50)
    print(f"\nProfitability Ratios:")
    for key, value in ratios.profitability.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nLiquidity Ratios:")
    for key, value in ratios.liquidity.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nLeverage Ratios:")
    for key, value in ratios.leverage.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nEfficiency Ratios:")
    for key, value in ratios.efficiency.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nValuation Ratios:")
    for key, value in ratios.valuation.items():
        print(f"  {key}: {value:.4f}")


if __name__ == '__main__':
    main()
