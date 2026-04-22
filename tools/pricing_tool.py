"""
Pricing Tool - Returns formatted pricing information for Inflix.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


PRICING_DATA = {
    "plans": [
        {
            "name": "Starter",
            "price": 29,
            "billing": "month",
            "description": "Perfect for individuals and small businesses",
            "features": [
                "Up to 5 social accounts",
                "30 scheduled posts per month",
                "Basic analytics dashboard",
                "AI caption generation (50 credits/month)",
                "Email support",
                "14-day free trial"
            ]
        },
        {
            "name": "Growth",
            "price": 79,
            "billing": "month",
            "description": "For growing businesses and marketing teams",
            "features": [
                "Up to 15 social accounts",
                "Unlimited scheduled posts",
                "Advanced analytics + competitor tracking",
                "AI content generation (500 credits/month)",
                "Priority email and live chat support",
                "Up to 3 team members",
                "Content calendar",
                "14-day free trial"
            ],
            "most_popular": True
        },
        {
            "name": "Enterprise",
            "price": None,
            "billing": "custom",
            "description": "For agencies and large organizations",
            "features": [
                "Unlimited social accounts",
                "Unlimited posts and AI credits",
                "Custom AI model fine-tuning",
                "Dedicated account manager",
                "SSO and advanced security",
                "Full API access",
                "Custom integrations"
            ]
        }
    ],
    "annual_discount": "20% off with annual billing",
    "free_trial": "14-day free trial on all plans, no credit card required"
}


class PricingTool:
    """Tool for retrieving and formatting Inflix pricing information."""
    
    def get_pricing(self, plan_name=None):
        """
        Get formatted pricing information.
        
        Args:
            plan_name: Specific plan to get info for (optional)
            
        Returns:
            Formatted pricing string
        """
        if plan_name:
            return self._get_plan_details(plan_name)
        return self._get_all_plans()
    
    def _get_all_plans(self):
        """Get formatted pricing for all plans."""
        lines = ["**Inflix Pricing Plans**\n"]
        
        for p in PRICING_DATA["plans"]:
            if p["price"]:
                price_str = f"${p['price']}/{p['billing']}"
            else:
                price_str = "Custom pricing"
            popular = " (Most Popular)" if p.get("most_popular") else ""
            
            lines.append(f"**{p['name']} Plan - {price_str}**{popular}")
            lines.append(f"_{p['description']}_")
            
            for feature in p["features"][:4]:
                lines.append(f"  - {feature}")
            
            if len(p["features"]) > 4:
                lines.append(f"  + {len(p['features']) - 4} more features")
            
            lines.append("")
        
        lines.append(f"Note: {PRICING_DATA['annual_discount']}")
        lines.append(f"Free Trial: {PRICING_DATA['free_trial']}")
        
        return "\n".join(lines)
    
    def _get_plan_details(self, plan_name):
        """Get detailed info for a specific plan."""
        for p in PRICING_DATA["plans"]:tools/pricing_tool.py
            if p["name"].lower() == plan_name.lower():
                if p["price"]:
                    price_str = f"${p['price']}/{p['billing']}"
                else:
                    price_str = "Custom pricing"
                lines = [
                    f"**{p['name']} Plan - {price_str}**",
                    f"_{p['description']}_",
                    "\nFeatures:"
                ]
                for feature in p["features"]:
                    lines.append(f"  - {feature}")
                return "\n".join(lines)
        return self._get_all_plans()

    def get_plan_comparison(self):
        """Get structured plan comparison data."""
        return PRICING_DATA
