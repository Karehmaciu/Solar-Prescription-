# Quick Start Guide - Solar Prescription

## Get Running in 5 Minutes

### Step 1: Get Your API Key (2 minutes)
1. Go to https://developer.nrel.gov/signup/
2. Fill in your email
3. You'll receive an API key immediately
4. Copy it

### Step 2: Configure (1 minute)
1. Open `.env` file
2. Replace `your_api_key_here` with your actual key:
   ```
   NREL_API_KEY=your_actual_key_goes_here
   ```
3. Save the file

### Step 3: Install & Run (2 minutes)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

### Step 4: Test It
1. Open browser: http://localhost:5000
2. Try location: "Nairobi"
3. Select kit: "300W"
4. Pick appliances: LED Bulbs, Phone Charger, Small TV
5. Click "Get My Prescription"

## Example Test Case

**Location**: Nairobi, Kenya (great sun)
**Kit**: 300W
**Appliances**: 
- 3 LED Bulbs
- 2 Phone Chargers
- 1 Small TV

**Expected Result**: ✓ Approved (kit produces ~1200 Wh/day, need ~370 Wh/day)

---

**Location**: Oslo, Norway (poor sun in winter)
**Kit**: 300W
**Appliances**: Same as above

**Expected Result**: ⚠ Warning or ✗ Rejected (seasonal variation too high)

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key error"
- Check your .env file
- Make sure NREL_API_KEY is set correctly
- No spaces around the = sign

### "Port already in use"
Edit `app.py`, change last line:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

## Deployment (Optional)

### Deploy to Render.com (Free)
1. Create account on Render.com
2. Connect your GitHub repo
3. Add environment variable: `NREL_API_KEY`
4. Deploy!

### Deploy to Heroku
```bash
# Add Procfile
echo "web: python app.py" > Procfile

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create
heroku config:set NREL_API_KEY=your_key
git push heroku main
```

## Next Steps

1. **Add More Cities**: Edit `static/js/main.js`, add to `COMMON_LOCATIONS`
2. **Customize Appliances**: Edit `prescription_engine.py`, update `APPLIANCE_SPECS`
3. **Change Styling**: Edit `static/css/styles.css`
4. **Add Languages**: Create new template files

## Need Help?

Check the full README.md for detailed documentation.
