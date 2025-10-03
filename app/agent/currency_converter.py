# app/agent/currency_converter.py
from typing import Optional, Tuple
import requests
from datetime import datetime, timedelta
import os

class CurrencyConverter:
    """
    Handles currency and unit conversions for financial data extraction.
    """
    
    # Cache exchange rate to avoid frequent API calls
    _cached_rate: Optional[float] = None
    _cache_timestamp: Optional[datetime] = None
    _cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    @classmethod
    def get_inr_to_usd_rate(cls) -> float:
        """
        Get current INR to USD exchange rate.
        Uses a fallback rate if API is unavailable.
        """
        # Check if we have a valid cached rate
        if (cls._cached_rate and cls._cache_timestamp and 
            datetime.now() - cls._cache_timestamp < cls._cache_duration):
            return cls._cached_rate
        
        try:
            # Try to get live rate from a free API
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/INR",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                rate = data['rates']['USD']
                
                # Cache the rate
                cls._cached_rate = rate
                cls._cache_timestamp = datetime.now()
                print(f"Updated INR to USD rate: {rate}")
                return rate
        except Exception as e:
            print(f"Failed to fetch live exchange rate: {e}")
        
        # Fallback to approximate rate (as of 2024)
        fallback_rate = 0.012  # 1 INR ≈ 0.012 USD
        print(f"Using fallback INR to USD rate: {fallback_rate}")
        return fallback_rate
    
    @classmethod
    def convert_inr_crores_to_usd_billion(cls, inr_crores: float) -> Tuple[float, str]:
        """
        Convert INR Crores to USD Billion.
        
        1 Crore = 10 million
        1 Billion = 1000 million
        So: 1 Crore = 0.01 Billion
        
        Returns: (converted_value, unit)
        """
        usd_rate = cls.get_inr_to_usd_rate()
        
        # Convert Crores to USD
        usd_crores = inr_crores * usd_rate
        
        # Convert Crores to Billion (1 Crore = 0.01 Billion)
        usd_billion = usd_crores * 0.01
        
        return round(usd_billion, 2), "USD Billion"
    
    @classmethod
    def convert_inr_to_usd(cls, inr_value: float) -> Tuple[float, str]:
        """
        Convert INR to USD.
        
        Returns: (converted_value, unit)
        """
        usd_rate = cls.get_inr_to_usd_rate()
        usd_value = inr_value * usd_rate
        
        return round(usd_value, 2), "USD"
    
    @classmethod
    def should_convert_currency(cls, found_unit: str, required_unit: str) -> bool:
        """
        Determine if currency conversion is needed.
        """
        found_lower = found_unit.lower()
        required_lower = required_unit.lower()
        
        # Check for INR → USD conversions
        if "inr" in found_lower and "usd" in required_lower:
            return True
        if "₹" in found_unit and "usd" in required_lower:
            return True
        if "crore" in found_lower and "usd billion" in required_lower:
            return True
            
        return False
    
    @classmethod
    def perform_conversion(cls, value: float, from_unit: str, to_unit: str) -> Tuple[float, str]:
        """
        Perform the appropriate conversion based on units.
        
        Returns: (converted_value, converted_unit)
        """
        from_lower = from_unit.lower()
        to_lower = to_unit.lower()
        
        # INR Crores → USD Billion
        if "crore" in from_lower and "usd billion" in to_lower:
            return cls.convert_inr_crores_to_usd_billion(value)
        
        # INR → USD (for individual values like EPS)
        elif "inr" in from_lower and "usd" in to_lower:
            return cls.convert_inr_to_usd(value)
        
        # ₹ crore → USD Billion (alternative format)
        elif "₹" in from_unit and "crore" in from_lower and "usd billion" in to_lower:
            return cls.convert_inr_crores_to_usd_billion(value)
        
        # If no conversion rule matches, return original
        return value, from_unit

# Test the converter
if __name__ == "__main__":
    converter = CurrencyConverter()
    
    # Test INR Crores to USD Billion
    print("Testing INR Crores to USD Billion conversion:")
    test_value = 255324  # INR Crores from TCS report
    converted_value, unit = converter.convert_inr_crores_to_usd_billion(test_value)
    print(f"{test_value} INR Crores = {converted_value} {unit}")
    
    # Test INR to USD
    print("\nTesting INR to USD conversion:")
    test_eps = 134.19  # INR EPS from TCS report
    converted_eps, eps_unit = converter.convert_inr_to_usd(test_eps)
    print(f"{test_eps} INR = {converted_eps} {eps_unit}")
