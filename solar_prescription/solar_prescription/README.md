# Solar Prescription Initiative

## 🌍 Mission

**Stop selling solar kits globally without location warnings.**

Just like medicine, solar kits should be prescribed based on where you live - not sold as a one-size-fits-all solution. A 300W kit in Nairobi, Kenya produces 40% more power than the same kit in Oslo, Norway. Yet manufacturers market these kits globally with no location-specific warnings.

This app protects consumers by providing honest, location-specific recommendations before they buy.

## 💡 The Problem

1. **Global Marketing, Local Reality**: Solar kits are advertised with wattage ratings (100W, 300W, 1000W) that suggest consistent performance everywhere
2. **No Location Warnings**: Manufacturers don't warn buyers that the same kit performs drastically differently in different regions
3. **Disappointed Customers**: People in low-irradiance regions buy kits that can't meet their needs
4. **No Transparency**: Industry lacks tools to help consumers make informed decisions

## ✅ Our Solution

The Solar Prescription model:

- **Location-First**: Uses real NASA satellite data (via NREL PVWatts) to calculate actual production in your location
- **Simple Interface**: No technical knowledge required - just city, kit size, and what you need to power
- **Clear Verdicts**: Yes, Warning, or No - with specific reasons and alternatives
- **Consumer Protection**: Warns about seasonal variations and low-irradiance regions
- **Transparent**: Shows all calculations and assumptions

## 🚀 Features

- **Smart Location Search**: Type your city, we handle the coordinates
- **Kit Size Selection**: 50W to 1000W range (typical consumer kits)
- **Simple Appliance Picker**: No watts/hours calculations - just select what you'll use
- **Real Solar Data**: PVWatts API provides location-specific production estimates
- **Verdict System**: 
  - ✓ **Approved**: Kit will work reliably
  - ⚠ **Warning**: Will work most months, but expect shortages
  - ✗ **Rejected**: Kit too small, specific recommendation provided
- **Seasonal Analysis**: Shows best/worst month production
- **Clear Recommendations**: Suggests alternative kit sizes when needed

## 📋 How It Works

1. **User Input**:
   - Location (city name)
   - Kit size they're considering
   - Appliances they want to power

2. **Backend Calculation**:
   - Fetches real irradiance data from PVWatts API
   - Calculates daily energy production for that location
   - Calculates daily energy need from appliances
   - Accounts for 20% system losses (battery, inverter, wiring)
   - Analyzes seasonal variation

3. **Prescription**:
   - Compares production vs. need
   - Generates verdict (approved/warning/rejected)
   - Provides warnings for low-irradiance or high-variation regions
   - Suggests alternatives if current kit won't work

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- NREL API Key (free): https://developer.nrel.gov/signup/

### Setup

1. **Clone/Download** this repository

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.template .env
```

Edit `.env` and add your NREL API key:
```
NREL_API_KEY=your_actual_api_key_here
```

4. **Run the app**:
```bash
python app.py
```

5. **Open browser**:
```
http://localhost:5000
```

## 📁 Project Structure

```
solar_prescription/
├── app.py                      # Main Flask application
├── prescription_engine.py      # Core recommendation logic
├── pvwatts.py                  # NREL API integration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── templates/
│   ├── index.html             # Main form page
│   └── results.html           # Prescription results
├── static/
│   ├── css/
│   │   └── styles.css         # All styling
│   └── js/
│       └── main.js            # Frontend interactions
└── README.md                  # This file
```

## 🎯 Target Users

1. **Kit Buyers**: People considering small solar kits (10W-1000W)
2. **Installers**: Professionals who want quick guidance for customers
3. **NGOs/Aid Organizations**: Distributing solar kits in developing regions
4. **Policy Makers**: Understanding regional solar potential

## 📊 Data Source

We use **NREL PVWatts Version 8**:
- Real NASA satellite data
- 4km spatial resolution
- Updated through 2020
- ±10% annual accuracy for well-matched systems
- Validated against thousands of real installations

## 🔬 Technical Details

### Energy Calculation

**Daily Energy Need** = Σ (Appliance Watts × Hours per day × Quantity)

**Example**:
- 3 LED bulbs (10W × 5h × 3) = 150 Wh
- 1 phone charger (10W × 2h × 1) = 20 Wh
- 1 small TV (50W × 4h × 1) = 200 Wh
- **Total = 370 Wh/day**

### Production Calculation

Via PVWatts API:
- Location coordinates
- Kit size (in kW)
- Standard module type
- Roof-mounted configuration
- Tilt = latitude
- Azimuth = 180° (south) or 0° (based on hemisphere)
- 14% system losses

**Returns**: Monthly and annual kWh production

### Verdict Logic

After accounting for 20% additional losses (battery, inverter):

- **Excellent**: Production ≥ 120% of need
- **Good**: Production ≥ 100% AND worst month ≥ 80%
- **Marginal**: Production ≥ 80% OR worst month ≥ 60%
- **Insufficient**: Below marginal thresholds

## ⚠️ Important Notes

1. **Estimates Only**: Results are estimates. Actual performance depends on:
   - Installation quality
   - Shading
   - Maintenance
   - Component quality

2. **System Losses**: We account for 20% real-world losses (conservative estimate)

3. **Weather Variation**: Based on typical meteorological year - actual weather varies

4. **Not Professional Design**: This tool is for preliminary assessment only. Professional installations should use detailed modeling tools.

## 🤝 Contributing

This is an advocacy project. Contributions welcome:

- Add more cities to location database
- Improve UI/UX
- Add multi-language support
- Create educational content
- Report bugs or issues

## 📄 License

MIT License - Free to use and modify

## 🌟 Vision

**Every solar kit sold globally should come with location-specific performance data.**

We're building transparency into an industry that desperately needs it. Solar is amazing technology, but only when matched correctly to location and need.

## 📞 Contact

Built by Maina - Solar Energy Professional

Part of the **Solar Prescription Initiative**
- 10+ years in solar industry (East & West Africa)
- Trained 100+ solar technicians
- Advocate for consumer protection in renewable energy

## 🙏 Acknowledgments

- **NREL**: For providing free access to PVWatts API
- **NASA**: For satellite irradiance data
- **Solar Industry**: Colleagues who've shared real-world insights

---

**Remember**: A solar kit is not just a product. It's a prescription for your location's solar resource. Get it right.
