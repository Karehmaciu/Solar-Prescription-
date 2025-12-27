"""
Quick test script for Solar Prescription Engine
Run this to verify core functionality before starting the web app
"""

from prescription_engine import SolarPrescription

# Sample PVWatts data (realistic for Nairobi)
sample_pvwatts_data = {
    'outputs': {
        'ac_annual': 438,  # kWh per year for a 300W system
        'ac_monthly': [
            35.8, 36.4, 38.9, 36.1, 33.2, 31.8,
            30.6, 32.1, 34.3, 36.7, 35.9, 36.2
        ]
    }
}

# Test case: 300W kit in Nairobi
print("=" * 60)
print("SOLAR PRESCRIPTION ENGINE TEST")
print("=" * 60)
print()

engine = SolarPrescription()

# Test 1: Energy calculation
print("Test 1: Energy Need Calculation")
print("-" * 60)
appliances = [
    {'id': 'led_bulb', 'quantity': 3},
    {'id': 'phone_charger', 'quantity': 2},
    {'id': 'small_tv', 'quantity': 1}
]

daily_need, details = engine.calculate_daily_energy_need(appliances)
print(f"Daily Energy Need: {daily_need} Wh")
for app in details:
    print(f"  - {app['name']} x{app['quantity']}: {app['daily_wh']} Wh")
print()

# Test 2: Production calculation
print("Test 2: Production Calculation")
print("-" * 60)
production = engine.get_daily_production(sample_pvwatts_data, 300)
print(f"Daily Average: {production['daily_avg']:.0f} Wh")
print(f"Best Month: {production['best_month_daily']:.0f} Wh/day")
print(f"Worst Month: {production['worst_month_daily']:.0f} Wh/day")
print()

# Test 3: Verdict
print("Test 3: Verdict Determination")
print("-" * 60)
verdict = engine.determine_verdict(production, daily_need)
print(f"Verdict: {verdict['verdict'].upper()}")
print(f"Average Coverage: {verdict['avg_coverage']}%")
print(f"Worst Month Coverage: {verdict['worst_coverage']}%")
print()

# Test 4: Full prescription
print("Test 4: Complete Prescription")
print("-" * 60)
prescription = engine.generate_prescription(
    location="Nairobi, Kenya",
    latitude=-1.2921,
    longitude=36.8219,
    kit_size=300,
    appliances=appliances,
    pvwatts_data=sample_pvwatts_data
)

print(f"Status: {prescription['recommendation']['status'].upper()}")
print(f"Title: {prescription['recommendation']['title']}")
print(f"Message: {prescription['recommendation']['message']}")
print()

if prescription['recommendation']['warnings']:
    print("Warnings:")
    for warning in prescription['recommendation']['warnings']:
        print(f"  - {warning}")
print()

print("=" * 60)
print("✓ All tests completed successfully!")
print("=" * 60)
print()
print("Next step: Run the web app with 'python app.py'")
