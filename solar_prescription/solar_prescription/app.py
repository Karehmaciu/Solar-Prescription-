from flask import Flask, render_template, request, jsonify, session, redirect
import os
from datetime import datetime
from prescription_engine import SolarPrescription
from pvwatts import get_pvwatts_data
import secrets
from dotenv import load_dotenv
import requests
import csv
import re

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Debug: print status at startup (but not the actual keys)
if os.path.exists(env_path):
    print(f"Loaded .env from: {env_path}")
print(f"Weather API key loaded: {bool(WEATHER_API_KEY)}")
print(f"NREL API key loaded: {bool(os.getenv('NREL_API_KEY'))}")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(16)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# When hosted on Render, the app is served behind HTTPS.
if os.getenv("RENDER"):
    app.config.update(SESSION_COOKIE_SECURE=True)


def _extract_recommended_watts(prescription: dict) -> int | None:
    recommendation = (prescription or {}).get("recommendation") or {}
    suggestion = recommendation.get("suggestion")
    if not suggestion or not isinstance(suggestion, str):
        return None
    match = re.search(r"(\d+)\s*W", suggestion, flags=re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


@app.route("/")
def index():
    """Main landing page"""
    return render_template("index.html")


@app.route("/prescribe", methods=["POST"])
def prescribe():
    """Main prescription endpoint"""
    try:
        data = request.json

        # Extract user inputs
        location = data.get("location")
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
        kit_size = int(data.get("kit_size", 0))
        coverage_percentage = int(data.get("coverage_percentage", 70))  # Default 70%
        appliances = data.get("appliances", [])

        # Initialize prescription engine
        engine = SolarPrescription()

        # Calculate optimal tilt (use 15° minimum for near-equator locations)
        optimal_tilt = max(15, abs(latitude))

        # Calculate azimuth: 180° (south) for Northern Hemisphere, 0° (north) for Southern
        # But use 180° for locations very close to equator (within 5°)
        if abs(latitude) < 5:
            azimuth = 180  # Default to south-facing near equator
        else:
            azimuth = 180 if latitude >= 0 else 0

        # If no kit size selected, calculate the recommended minimum
        if kit_size == 0:
            # Use a small but valid capacity for PVWatts
            dummy_kit_size = 100
            dummy_system_capacity_kw = dummy_kit_size / 1000

            # Get PVWatts data for dummy capacity
            pvwatts_data_dummy, error = get_pvwatts_data(
                system_capacity=dummy_system_capacity_kw,
                module_type=0,  # Standard
                array_type=1,  # Fixed - Roof Mounted
                tilt=optimal_tilt,
                azimuth=azimuth,
                lat=latitude,
                lon=longitude,
                losses=14,  # Default losses
            )

            if error or not pvwatts_data_dummy:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Could not fetch solar data for this location. Please try again.",
                        }
                    ),
                    400,
                )

            # Get dummy prescription to calculate energy needs
            prescription_dummy = engine.generate_prescription(
                location=location,
                latitude=latitude,
                longitude=longitude,
                kit_size=dummy_kit_size,
                appliances=appliances,
                pvwatts_data=pvwatts_data_dummy,
            )

            daily_wh = float(prescription_dummy["energy_need"]["daily_wh"])

            # PVWatts monthly outputs are in kWh for the whole system.
            monthly_kwh = (pvwatts_data_dummy.get("outputs") or {}).get(
                "ac_monthly"
            ) or []
            if not monthly_kwh:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Could not fetch solar data for this location. Please try again.",
                        }
                    ),
                    400,
                )

            worst_month_daily_wh_system = (min(monthly_kwh) * 1000) / 30
            worst_month_daily_wh_per_w = worst_month_daily_wh_system / dummy_kit_size

            # Calculate needed capacity with safety margins
            # Needed kW = (daily_wh * 1.2 safety factor) / (wh_per_w * 0.8 efficiency factor)
            needed_watts = (daily_wh * 1.2) / max(
                0.001, (worst_month_daily_wh_per_w * 0.8)
            )

            # Round up to standard sizes
            standard_sizes = [10, 20, 50, 100, 200, 300, 500, 1000]
            for size in standard_sizes:
                if size >= needed_watts:
                    kit_size = size
                    break
            else:
                kit_size = 1000

        # Get PVWatts data for this location
        # Convert kit size to kW (kit is in Watts)
        system_capacity_kw = kit_size / 1000

        # NREL API has minimum system capacity of ~0.05 kW (50W)
        # For smaller systems, use 0.1 kW and scale results proportionally
        actual_capacity = system_capacity_kw
        if system_capacity_kw < 0.05:
            system_capacity_kw = 0.1  # Use minimum viable capacity for API

        pvwatts_data, error = get_pvwatts_data(
            system_capacity=system_capacity_kw,
            module_type=0,  # Standard
            array_type=1,  # Fixed - Roof Mounted
            tilt=optimal_tilt,
            azimuth=azimuth,
            lat=latitude,
            lon=longitude,
            losses=14,  # Default losses
        )

        if error or not pvwatts_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Could not fetch solar data for this location. Please try again.",
                    }
                ),
                400,
            )

        # Scale results if we used a larger capacity than requested
        if actual_capacity < 0.05 and "outputs" in pvwatts_data:
            scale_factor = actual_capacity / system_capacity_kw
            outputs = pvwatts_data["outputs"]
            # Scale the energy outputs
            if "ac_annual" in outputs:
                outputs["ac_annual"] *= scale_factor
            if "ac_monthly" in outputs:
                outputs["ac_monthly"] = [
                    x * scale_factor for x in outputs["ac_monthly"]
                ]
            if "dc_monthly" in outputs:
                outputs["dc_monthly"] = [
                    x * scale_factor for x in outputs["dc_monthly"]
                ]

        # Calculate prescription
        prescription = engine.generate_prescription(
            location=location,
            latitude=latitude,
            longitude=longitude,
            kit_size=kit_size,
            appliances=appliances,
            pvwatts_data=pvwatts_data,
            coverage_percentage=coverage_percentage,
        )

        # Extract recommended wattage from suggestion if present
        recommended_watts = _extract_recommended_watts(prescription)

        # Store in session for results page
        session["prescription"] = prescription
        session["location"] = location
        session["recommended_watts"] = recommended_watts
        session["coverage_percentage"] = coverage_percentage

        return jsonify({"success": True, "prescription": prescription})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/results")
def results():
    """Results page showing prescription details"""
    prescription = session.get("prescription")
    location = session.get("location")
    coverage_percentage = session.get("coverage_percentage", 70)

    if not prescription:
        return redirect("/")

    suggestion_prefix = None
    suggestion_suffix = None
    suggestion_watts = None
    suggestion_watts_text = None
    suggestion = ((prescription or {}).get("recommendation") or {}).get("suggestion")
    if isinstance(suggestion, str) and suggestion:
        match = re.search(r"(\d+)\s*W", suggestion, flags=re.IGNORECASE)
        if match:
            suggestion_prefix = suggestion[: match.start()]
            suggestion_suffix = suggestion[match.end() :]
            suggestion_watts = int(match.group(1))
            suggestion_watts_text = f"{suggestion_watts}W"

    # Prefer the recommended size (if any) for browsing products.
    browse_watts = _extract_recommended_watts(prescription)
    browse_is_fallback = False
    if not browse_watts:
        browse_watts = (prescription or {}).get("kit_size") or 50
        browse_is_fallback = True

    # Check if recommended kit is outside certified range (max 160W)
    MAX_CERTIFIED_WATTS = 160
    is_outside_certified_range = False
    if browse_watts and browse_watts > MAX_CERTIFIED_WATTS:
        is_outside_certified_range = True

    # Coverage explanation based on percentage
    coverage_explanations = {
        50: {
            "title": "50% Coverage - Budget Option",
            "description": "You'll have reliable power for about 6 months of the year. During low-sun months (rainy season), expect reduced performance or outages.",
            "recommendation": "Consider having a backup plan (like reducing usage or having alternative power) during worst weather months.",
        },
        70: {
            "title": "70% Coverage - Balanced Choice",
            "description": "You'll have reliable power for most of the year (about 8-9 months). Some reduced performance expected during worst weather months.",
            "recommendation": "Monitor your usage during rainy season and be ready to reduce non-essential loads if needed.",
        },
        90: {
            "title": "90% Coverage - Premium Reliability",
            "description": "You'll have reliable power year-round, including during worst weather months. Maximum confidence in your solar system.",
            "recommendation": "Your system is designed for consistent performance even during challenging weather conditions.",
        },
    }
    coverage_info = coverage_explanations.get(
        coverage_percentage, coverage_explanations[70]
    )

    return render_template(
        "results.html",
        prescription=prescription,
        location=location,
        browse_watts=browse_watts,
        browse_is_fallback=browse_is_fallback,
        suggestion_prefix=suggestion_prefix,
        suggestion_suffix=suggestion_suffix,
        suggestion_watts=suggestion_watts,
        suggestion_watts_text=suggestion_watts_text,
        coverage_percentage=coverage_percentage,
        coverage_info=coverage_info,
        is_outside_certified_range=is_outside_certified_range,
        max_certified_watts=MAX_CERTIFIED_WATTS,
    )


@app.route("/api/geocode")
def geocode():
    """Location autocomplete using Nominatim (OpenStreetMap) - free, no API key needed.

    Returns a dict of display_name -> {lat, lon}.
    This endpoint intentionally does not hardcode towns/cities.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({})

    try:
        # Use Nominatim (OpenStreetMap) - free geocoding service
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "SolarPrescriptionApp/1.0"}
        params = {"q": query, "format": "json", "limit": 8, "addressdetails": 1}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return jsonify({})

        results = response.json() or []
        matches = {}
        for item in results[:8]:
            lat = item.get("lat")
            lon = item.get("lon")

            if lat is not None and lon is not None:
                # Build display name from address components
                address = item.get("address", {})
                name_parts = []

                # Prefer town/village/city
                for key in ["town", "village", "city", "county", "state", "country"]:
                    val = address.get(key)
                    if val and val not in name_parts:
                        name_parts.append(val)

                if name_parts:
                    display_name = ", ".join(name_parts)
                else:
                    display_name = item.get("display_name", "Unknown")

                matches[display_name] = {"lat": float(lat), "lon": float(lon)}

        return jsonify(matches)
    except Exception as e:
        print(f"Geocoding error: {e}")
        return jsonify({})


@app.route("/products")
def products():
    """Browse certified VeraSol products by wattage"""
    watts = request.args.get("watts", type=int)
    if not watts:
        return render_template("products.html", products=None, watts=None)

    try:
        # Load the CSV
        csv_path = os.path.join(
            os.path.dirname(__file__), "data", "all_solar_kits_combined.csv"
        )

        products_list: list[dict] = []
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_power = row.get("PV Module Maximum Power [W]")
                if raw_power is None:
                    continue
                try:
                    power = int(float(str(raw_power).strip()))
                except (TypeError, ValueError):
                    continue
                if power == watts:
                    products_list.append(row)

        return render_template("products.html", products=products_list, watts=watts)
    except Exception as e:
        print(f"Error loading products: {e}")
        return render_template(
            "products.html", products=None, watts=watts, error=str(e)
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug_env = os.environ.get("FLASK_DEBUG")
    debug = (debug_env or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    # Default to debug=True for local development unless explicitly disabled.
    if debug_env is None or not str(debug_env).strip():
        debug = True
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
