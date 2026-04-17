import math

class MortgageCalculator:
    # Tasas reales estimadas para Polonia (Abril 2026)
    # WIBOR 3M/6M (~3.75%) + Margen de Banco (~2.0%) = 5.75%
    DEFAULT_ANNUAL_INTEREST_RATE = 0.0575
    DEFAULT_DOWN_PAYMENT_PCT = 0.20 # 20% inicial
    
    @staticmethod
    def calculate_monthly_payment(price: float, term_years: int, down_payment_pct: float = 0.20, annual_rate: float = 0.0575) -> float:
        """
        Calcula la cuota mensual usando la fórmula de anualidad.
        P = [r * PV] / [1 - (1 + r)^-n]
        """
        if price <= 0: return 0
        
        down_payment = price * down_payment_pct
        loan_amount = price - down_payment
        
        monthly_rate = annual_rate / 12
        num_payments = term_years * 12
        
        if monthly_rate == 0:
            return loan_amount / num_payments
            
        payment = (monthly_rate * loan_amount) / (1 - math.pow(1 + monthly_rate, -num_payments))
        return payment

    @staticmethod
    def get_market_context() -> str:
        return f"Basado en tasas de Polonia (Abril 2026): WIBOR/Base ~3.75% + Margen ~2.0% = TOTAL {MortgageCalculator.DEFAULT_ANNUAL_INTEREST_RATE*100:.2f}%"

if __name__ == "__main__":
    # Test
    p = 800000
    print(f"Precio: {p} PLN")
    print(f"Cuota 20 años: {MortgageCalculator.calculate_monthly_payment(p, 20):,.2f} PLN")
    print(f"Cuota 30 años: {MortgageCalculator.calculate_monthly_payment(p, 30):,.2f} PLN")
