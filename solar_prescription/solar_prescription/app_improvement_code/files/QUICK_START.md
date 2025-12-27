# Quick Start: Solar Prescription + VeraSol Integration

## What You're Getting

Your Solar Prescription app now shows **certified VeraSol products** that will work in the user's location!

## 3-Minute Setup

### 1. Extract the Package
```bash
tar -xzf solar_prescription_with_verasol.tar.gz
cd solar_prescription
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

Requirements are:
- Flask
- pandas (NEW - for VeraSol database)
- requests (for NREL API)
- python-dotenv

### 3. Set Your API Key
```bash
cp .env.template .env
nano .env  # Add your NREL API key
```

### 4. Run the App
```bash
python app.py
```

Visit: http://localhost:5000

## What Changed

### New Features ✨
1. **VeraSol Product Matching** - Shows certified products for user's location
2. **Visual Product Cards** - Easy-to-read product information
3. **Coverage Analysis** - Shows which products will work 85%+ year-round
4. **Smart Filtering** - Only shows products that match needs

### Files Added
- `verasol_matcher.py` - Product matching engine
- `data/all_solar_kits_combined.csv` - 183 certified products
- `VERASOL_INTEGRATION.md` - Full documentation

### Files Modified  
- `app.py` - Added product matching
- `templates/results.html` - Added product display section
- `static/css/styles.css` - Added product card styles

## How It Works

**User Journey:**
1. Enter location (e.g., "Nairobi")
2. Select kit size they're considering
3. Click appliances they need (visual selection)
4. Get prescription + matching certified products

**Behind the Scenes:**
```
Location → NREL API → Solar production data
Appliances → Calculate daily energy need
VeraSol DB → Filter products that work 85%+ in worst month
Results → Show prescription + certified products
```

## Example Output

**User selects:**
- Location: Embu, Kenya  
- 2 LED lights, 1 phone  
- Considering 10W kit

**App shows:**
1. Verdict: ⚠ This kit is marginal
2. Your need: 40 Wh/day
3. Kit production: 33 Wh/day average, 25 Wh worst month
4. **Certified products that work:** StarTimes S50C (14W), LEMI Solar Home (10W), etc.

## Testing Different Scenarios

Try these to see it in action:

**Scenario 1: Rural Home**
- Location: Kisumu, Kenya
- 3 LED lights, 2 phones, 1 radio
- Try 100W kit
- Result: Shows multiple good matches

**Scenario 2: Small Business**  
- Location: Lagos, Nigeria
- 5 LED lights, 1 small TV, 2 phones
- Try 300W kit
- Result: Shows larger certified systems

**Scenario 3: Low Sun Region**
- Location: Cape Town, South Africa
- 2 LED lights, 1 phone
- Try 50W kit
- Result: May warn about seasonal variation

## Key Benefits

### For Users
- See certified products that actually work in their location
- No guessing if a kit is "good enough"
- Transparent worst-month coverage percentages

### For You
- Builds trust by recommending certified products
- Protects users from buying wrong kits
- Professional, data-driven recommendations

## Next Steps

Want to enhance it further?

1. **Add Images** - Product photos from manufacturers
2. **Add Pricing** - If you have distributor partnerships
3. **Add Buy Links** - Direct users to purchase
4. **Expand Database** - Add more certified products
5. **Add Filters** - Battery type, brand preference, etc.

## Database Info

**Current Database:**
- 183 certified products
- 62 brands
- 0.3W to 160W range
- All VeraSol verified

**To update:**
Download new data from https://data.verasol.org/ and replace the CSV file.

## Support

Questions? Check:
- `VERASOL_INTEGRATION.md` - Full technical docs
- `README.md` - Original app documentation
- `prescription_engine.py` - Calculation logic
- `verasol_matcher.py` - Product matching logic

## Important Notes

⚠️ **Remember:**
- This is for preliminary assessment only
- Actual performance varies with installation
- Always recommend professional installation
- Products shown are certified, but user should verify availability

✅ **Success Check:**
If you see certified products on the results page after filling the form, integration is working!

---

**Built by:** Maina  
**Project:** Solar Prescription Initiative  
**Goal:** Consumer protection through transparency
