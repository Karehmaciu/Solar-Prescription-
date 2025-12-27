"""
Solar Prescription Engine
Core logic for determining if a solar kit is suitable for a location and usage pattern
"""

import json
import os


class SolarPrescription:
    """
    Generates solar kit prescriptions based on location, kit size, and energy needs
    """

    def __init__(self):
        self.prescription = {}
        # Load product specifications from JSON file
        self.PRODUCT_SPECS = self._load_product_specs()

    def _load_product_specs(self):
        """Load product specifications from JSON file"""
        try:
            json_path = os.path.join(
                os.path.dirname(__file__), "products_specs", "products.json"
            )
            with open(json_path, "r") as f:
                specs = json.load(f)
                # Convert string keys to integers
                return {int(k): v for k, v in specs.items()}
        except Exception as e:
            print(f"Warning: Could not load product specs: {e}")
            # Fallback to basic spec for 10W
            return {
                10: {
                    "model": "SL1210",
                    "brand": "Shenzhen FengWo",
                    "type": "Pico PV System",
                    "battery": {
                        "voltage": 11.1,
                        "capacity_ah": 10,
                        "capacity_wh": 111,
                        "chemistry": "Li-ion",
                    },
                    "lights": {"count": 4, "lumens": 680, "runtime_hours": 13},
                    "ports": {"usb": 2, "barrel_jack": 3},
                    "features": [
                        "Phone charging",
                        "Radio support",
                        "4 LED lights",
                        "Plug-and-play",
                    ],
                    "daily_energy_available": 35,
                    "warranty_months": 12,
                    "verasol_certified": True,
                }
            }

    # Typical appliance power consumption (Watts)
    APPLIANCE_SPECS = {
        "led_bulb": {"watts": 10, "hours": 5, "label": "Household LED Bulb (10W)"},
        "kit_light": {"watts": 2, "hours": 5, "label": "Pico Kit Light Point (2W)"},
        "phone_charger": {"watts": 10, "hours": 2, "label": "Phone Charger"},
        "laptop": {"watts": 65, "hours": 4, "label": "Laptop"},
        "small_tv": {"watts": 50, "hours": 4, "label": 'Small TV (24")'},
        "large_tv": {"watts": 150, "hours": 4, "label": 'Large TV (42")'},
        "fan": {"watts": 75, "hours": 8, "label": "Fan"},
        "radio": {"watts": 10, "hours": 3, "label": "Radio"},
        "wifi_router": {"watts": 10, "hours": 24, "label": "WiFi Router"},
        "small_fridge": {"watts": 100, "hours": 24, "label": "Small Fridge (DC)"},
        "laptop_charger": {"watts": 45, "hours": 3, "label": "Laptop Charger"},
        "decoder": {"watts": 15, "hours": 4, "label": "TV Decoder"},
        "security_lights": {"watts": 20, "hours": 12, "label": "Security Lights"},
    }

    # Kit sizes we support (in Watts)
    # Include pico kits used in the UI and product specs.
    KIT_SIZES = [10, 20, 30, 50, 70, 100, 150, 200, 300, 500, 1000]

    def calculate_daily_energy_need(self, appliances):
        """
        Calculate total daily energy requirement from selected appliances
        Returns: Daily energy need in Wh
        """
        total_wh = 0
        appliance_details = []

        for app in appliances:
            app_id = app.get("id")
            quantity = app.get("quantity", 1)

            if app_id in self.APPLIANCE_SPECS:
                spec = self.APPLIANCE_SPECS[app_id]
                daily_wh = spec["watts"] * spec["hours"] * quantity
                total_wh += daily_wh

                appliance_details.append(
                    {
                        "name": spec["label"],
                        "quantity": quantity,
                        "watts": spec["watts"],
                        "hours": spec["hours"],
                        "daily_wh": daily_wh,
                    }
                )

        return total_wh, appliance_details

    def get_daily_production(self, pvwatts_data, kit_size):
        """
        Extract daily production from PVWatts data
        Returns: Average daily production in Wh, monthly breakdown
        """
        outputs = pvwatts_data.get("outputs", {})
        annual_kwh = outputs.get("ac_annual", 0)
        monthly_kwh = outputs.get("ac_monthly", [])

        # Convert to Wh
        annual_wh = annual_kwh * 1000
        daily_avg_wh = annual_wh / 365

        # Find best and worst months
        monthly_wh = [m * 1000 for m in monthly_kwh]
        best_month_wh = max(monthly_wh) / 30 if monthly_wh else 0
        worst_month_wh = min(monthly_wh) / 30 if monthly_wh else 0

        return {
            "daily_avg": daily_avg_wh,
            "best_month_daily": best_month_wh,
            "worst_month_daily": worst_month_wh,
            "annual_total": annual_wh,
            "monthly": monthly_wh,
        }

    def determine_verdict(
        self, production, need, kit_size=None, coverage_percentage=70
    ):
        """
        Determine if kit is suitable based on coverage percentage target

        Args:
            coverage_percentage: Target percentage (50, 70, or 90) of year for reliable coverage
        Returns: verdict ('excellent', 'good', 'marginal', 'insufficient')
        """
        # Account for system losses (inverter, battery, wiring = 20% total)
        usable_production = production["daily_avg"] * 0.8
        worst_month_usable = production["worst_month_daily"] * 0.8

        # Track if we used tested value instead of theoretical
        used_tested_value = False

        # For products with tested daily energy, use the LOWER of theoretical vs tested
        # This prevents over-promising on small kits
        if kit_size and kit_size in self.PRODUCT_SPECS:
            tested_energy = self.PRODUCT_SPECS[kit_size].get(
                "daily_energy_available", 0
            )
            if tested_energy > 0:
                # Tested values already account for real-world losses
                # Use tested value directly if it's lower than theoretical
                if tested_energy < usable_production:
                    usable_production = tested_energy
                    worst_month_usable = (
                        tested_energy * 0.9
                    )  # Assume 10% reduction in worst month
                    used_tested_value = True

        # Calculate coverage ratios
        avg_coverage = (usable_production / need * 100) if need > 0 else 0
        worst_coverage = (worst_month_usable / need * 100) if need > 0 else 0

        # Adjust thresholds based on coverage percentage target
        # For 50% coverage: customer accepts marginal performance much of the year
        # For 70% coverage: balanced approach (default)
        # For 90% coverage: premium reliability, higher thresholds

        if coverage_percentage == 50:
            # Lower thresholds - customer wants budget option
            if avg_coverage >= 80:
                verdict = "excellent"
            elif avg_coverage >= 60 and worst_coverage >= 40:
                verdict = "good"
            elif avg_coverage >= 50 or worst_coverage >= 30:
                verdict = "marginal"
            else:
                verdict = "insufficient"
        elif coverage_percentage == 90:
            # Higher thresholds - customer wants premium reliability
            if avg_coverage >= 150 and worst_coverage >= 100:
                verdict = "excellent"
            elif avg_coverage >= 120 and worst_coverage >= 90:
                verdict = "good"
            elif avg_coverage >= 100 or worst_coverage >= 80:
                verdict = "marginal"
            else:
                verdict = "insufficient"
        else:  # 70% (default balanced)
            if avg_coverage >= 120:
                verdict = "excellent"
            elif avg_coverage >= 100 and worst_coverage >= 80:
                verdict = "good"
            elif avg_coverage >= 80 or worst_coverage >= 60:
                verdict = "marginal"
            else:
                verdict = "insufficient"

        return {
            "verdict": verdict,
            "avg_coverage": round(avg_coverage, 1),
            "worst_coverage": round(worst_coverage, 1),
            "usable_daily": round(usable_production, 0),
            "worst_month_usable": round(worst_month_usable, 0),
            "used_tested_value": used_tested_value,
            "coverage_percentage": coverage_percentage,
        }

    def get_recommendation(
        self,
        verdict_info,
        need,
        kit_size,
        production,
        used_tested_value=False,
        coverage_percentage=70,
    ):
        """
        Generate human-readable recommendation

        Args:
            coverage_percentage: Target coverage percentage (50, 70, or 90)
        """
        verdict = verdict_info["verdict"]

        if verdict == "excellent":
            warnings = []
            if used_tested_value:
                warnings.append(
                    "Calculation based on real-world tested performance, not theoretical solar panel output"
                )

            return {
                "status": "approved",
                "title": "✓ This Kit Will Work Perfectly",
                "message": f"This {kit_size}W kit produces more than enough energy for your needs. You have a comfortable safety margin even during cloudy days.",
                "confidence": "high",
                "warnings": warnings,
            }

        elif verdict == "good":
            warnings = [
                "Consider reducing usage slightly during the worst month (typically rainy season)"
            ]
            if used_tested_value:
                warnings.append(
                    "Calculation based on real-world tested performance, not theoretical solar panel output"
                )

            return {
                "status": "approved",
                "title": "✓ This Kit Will Work",
                "message": f"This {kit_size}W kit meets your daily energy needs. Expect reliable performance year-round.",
                "confidence": "high",
                "warnings": warnings,
            }

        elif verdict == "marginal":
            warnings = [
                f'You\'ll get only {verdict_info["worst_coverage"]}% of your needs in the worst month',
                "Plan to reduce usage during rainy/cloudy periods",
                "Consider upgrading to the next kit size for better reliability",
            ]
            if used_tested_value:
                warnings.append(
                    "⚠ Based on real-world tested values - theoretical calculations showed higher but unrealistic performance"
                )

            # Suggest next size up
            next_size = self._get_next_kit_size(kit_size)

            return {
                "status": "warning",
                "title": "⚠ This Kit is Marginal",
                "message": f"This {kit_size}W kit will work most of the year, but you'll face shortages during low-sun months.",
                "confidence": "medium",
                "warnings": warnings,
                "suggestion": f"We recommend upgrading to a {next_size}W kit for year-round reliability",
            }

        else:  # insufficient
            # Calculate needed size
            # Size for reliability: base on worst-month usable energy, not annual average.
            needed_size = self._calculate_needed_size(
                need,
                current_kit=kit_size,
                current_kit_usable_wh_per_day=verdict_info.get("worst_month_usable", 0),
                production_is_already_usable=True,
            )

            warnings_list = [
                f'This kit only provides {verdict_info["avg_coverage"]}% of your daily needs',
                "You will experience frequent power shortages",
                "Batteries will discharge completely, reducing their lifespan",
            ]
            if used_tested_value:
                warnings_list.append(
                    "⚠ Based on real-world tested values - this kit cannot support your selected appliances"
                )

            return {
                "status": "rejected",
                "title": "✗ This Kit is Too Small",
                "message": f"This {kit_size}W kit cannot meet your energy needs. You need a larger system.",
                "confidence": "high",
                "warnings": warnings_list,
                "suggestion": f"Minimum recommended: {needed_size}W kit",
            }

    def _get_next_kit_size(self, current_size):
        """Get the next available kit size"""
        for size in self.KIT_SIZES:
            if size > current_size:
                return size
        return current_size * 1.5  # If no standard size, suggest 50% more

    def _calculate_needed_size(
        self,
        need,
        *,
        current_kit,
        current_kit_usable_wh_per_day,
        production_is_already_usable=False,
    ):
        """Calculate what kit size is actually needed.

        Uses the current kit's *usable* daily energy (ideally worst-month usable) to estimate
        the Wh/W performance, then scales up with a 20% safety margin.
        """
        if not current_kit or current_kit <= 0:
            return self.KIT_SIZES[-1]

        if not current_kit_usable_wh_per_day or current_kit_usable_wh_per_day <= 0:
            return self._get_next_kit_size(current_kit)

        # How much usable energy do we get per watt of kit size?
        usable_wh_per_watt = current_kit_usable_wh_per_day / current_kit

        # If the provided production is still *theoretical*, apply 20% system losses.
        # If it's already usable (loss-adjusted or product-tested), don't double-apply losses.
        loss_factor = 1.0 if production_is_already_usable else 0.8

        # What size do we need for the required energy (with 20% margin)?
        needed_watts = (need * 1.2) / (usable_wh_per_watt * loss_factor)

        # Round up to next standard size
        for size in self.KIT_SIZES:
            if size >= needed_watts:
                return size

        # If larger than our standard sizes, round to nearest 100W
        return int((needed_watts + 99) // 100 * 100)

    def generate_prescription(
        self,
        location,
        latitude,
        longitude,
        kit_size,
        appliances,
        pvwatts_data,
        coverage_percentage=70,
    ):
        """
        Main method to generate complete prescription

        Args:
            coverage_percentage: Target percentage (50, 70, or 90) of year to meet energy needs
        """
        # Calculate energy need
        daily_need, appliance_details = self.calculate_daily_energy_need(appliances)

        # Get production data
        production = self.get_daily_production(pvwatts_data, kit_size)

        # Determine verdict (pass kit_size and coverage_percentage to use tested values for small kits)
        verdict_info = self.determine_verdict(
            production, daily_need, kit_size, coverage_percentage
        )

        # Get recommendation
        recommendation = self.get_recommendation(
            verdict_info,
            daily_need,
            kit_size,
            production,
            used_tested_value=verdict_info.get("used_tested_value", False),
            coverage_percentage=coverage_percentage,
        )

        # Get irradiance warnings based on location
        irradiance_warnings = self._get_irradiance_warnings(latitude, production)

        # Get product specs if available
        product_info = None
        if kit_size in self.PRODUCT_SPECS:
            specs = self.PRODUCT_SPECS[kit_size]

            # Format ports information
            ports_list = []
            if "usb" in specs["ports"]:
                ports_list.append(f"{specs['ports']['usb']} USB")
            if "barrel_jack" in specs["ports"]:
                ports_list.append(f"{specs['ports']['barrel_jack']} Barrel Jack")
            if "dc" in specs["ports"]:
                ports_list.append(f"{specs['ports']['dc']} DC")
            if "ac" in specs["ports"]:
                ports_list.append(f"{specs['ports']['ac']} AC")

            product_info = {
                "model": specs["model"],
                "brand": specs["brand"],
                "type": specs["type"],
                "pv_watts": specs.get("pv_watts", kit_size),
                "battery": f"{specs['battery']['capacity_wh']}Wh ({specs['battery']['voltage']}V, {specs['battery']['capacity_ah']}Ah {specs['battery']['chemistry']})",
                "lights": f"{specs['lights']['count']} LEDs, {specs['lights']['lumens']} lumens",
                "runtime": f"{specs['lights']['runtime_hours']} hours",
                "ports": ", ".join(ports_list) if ports_list else "N/A",
                "features": specs["features"],
                "warranty": f"{specs['warranty_months']} months",
                "tested_daily_energy": specs["daily_energy_available"],
                "verasol_certified": specs.get("verasol_certified", False),
            }

        # Compile complete prescription
        prescription = {
            "location": {
                "name": location,
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
            },
            "kit_size": kit_size,
            "product_info": product_info,
            "energy_need": {
                "daily_wh": round(daily_need, 0),
                "appliances": appliance_details,
            },
            "production": {
                "daily_avg": round(
                    verdict_info["usable_daily"], 0
                ),  # Use actual usable value
                "theoretical_avg": round(
                    production["daily_avg"], 0
                ),  # Keep theoretical for reference
                "best_month": round(production["best_month_daily"], 0),
                "worst_month": round(production["worst_month_daily"], 0),
                "annual_kwh": round(production["annual_total"] / 1000, 0),
                "using_tested_value": verdict_info.get("used_tested_value", False),
            },
            "verdict": verdict_info,
            "recommendation": recommendation,
            "irradiance_warnings": irradiance_warnings,
            "timestamp": datetime.now().isoformat(),
        }

        return prescription

    def _get_irradiance_warnings(self, latitude, production):
        """
        Generate location-specific warnings based on irradiance
        """
        warnings = []

        # Low irradiance regions (far from equator, or low production)
        if abs(latitude) > 40:
            warnings.append(
                {
                    "level": "high",
                    "message": "Your location receives significantly less sun than equatorial regions. Solar kit performance will be notably lower than advertised.",
                }
            )
        elif abs(latitude) > 25:
            warnings.append(
                {
                    "level": "medium",
                    "message": "Your location has moderate seasonal variation in solar production. Winter months will see reduced performance.",
                }
            )

        # Check actual production variance
        variance = (
            (
                (production["best_month_daily"] - production["worst_month_daily"])
                / production["best_month_daily"]
                * 100
            )
            if production["best_month_daily"] > 0
            else 0
        )

        if variance > 40:
            warnings.append(
                {
                    "level": "high",
                    "message": f"High seasonal variation: Production drops {variance:.0f}% in worst month. Plan accordingly.",
                }
            )
        elif variance > 25:
            warnings.append(
                {
                    "level": "medium",
                    "message": f"Moderate seasonal variation: Expect {variance:.0f}% less production in rainy season.",
                }
            )

        return warnings


from datetime import datetime
