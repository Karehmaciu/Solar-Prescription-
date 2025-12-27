# Deployment Guide - Solar Prescription

## Option 1: Render.com (Recommended - Free Tier)

### Why Render?
- Free tier available
- Automatic HTTPS
- Easy environment variable management
- Auto-deploy from Git
- Good performance

### Steps:

1. **Prepare Repository**
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Solar Prescription app"
   ```

2. **Push to GitHub**
   - Create new repository on GitHub
   - Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/solar-prescription.git
   git push -u origin main
   ```

3. **Deploy on Render**
   - Go to https://render.com
   - Sign up/Login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: solar-prescription
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment Variables**: 
       - Add `NREL_API_KEY` = your_api_key
       - Add `FLASK_ENV` = production

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Your app will be live at: `https://solar-prescription.onrender.com`

### Update .env for Production

Render automatically uses environment variables, so you don't need .env in production.

---

## Option 2: Heroku

### Steps:

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Ubuntu
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Procfile**
   ```bash
   echo "web: python app.py" > Procfile
   ```

3. **Update app.py for Heroku**
   Change the last line in `app.py` to:
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(debug=False, host='0.0.0.0', port=port)
   ```

4. **Deploy**
   ```bash
   heroku login
   heroku create solar-prescription
   heroku config:set NREL_API_KEY=your_api_key
   git push heroku main
   heroku open
   ```

---

## Option 3: PythonAnywhere (Free Tier)

### Steps:

1. **Sign up** at https://www.pythonanywhere.com

2. **Upload your code**
   - Use Web tab → Add new web app
   - Choose Flask
   - Upload your files via Files tab

3. **Configure**
   - In Web tab, set:
     - Source code: `/home/yourusername/solar_prescription`
     - Working directory: same
   - Add NREL_API_KEY to .env file

4. **Install requirements**
   - Open Bash console
   ```bash
   cd ~/solar_prescription
   pip install --user -r requirements.txt
   ```

5. **Reload**
   - Click "Reload" in Web tab
   - Visit your site: `yourusername.pythonanywhere.com`

---

## Option 4: DigitalOcean App Platform

### Steps:

1. **Push code to GitHub** (see Render steps)

2. **Create App on DigitalOcean**
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Connect GitHub repository

3. **Configure**
   - Detected type: Python
   - Environment Variables:
     - `NREL_API_KEY` = your_key
     - `FLASK_ENV` = production

4. **Deploy**
   - Review and create
   - Your app will be live with HTTPS

**Cost**: Free tier available ($0/month with credits)

---

## Option 5: AWS EC2 (Advanced)

### Quick Setup:

1. **Launch EC2 Instance**
   - Ubuntu 22.04
   - t2.micro (free tier)

2. **SSH and Install**
   ```bash
   ssh ubuntu@your-ec2-ip
   
   # Install Python and dependencies
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   
   # Clone your repo
   git clone your-repo-url
   cd solar_prescription
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/solar_prescription
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable and Run**
   ```bash
   sudo ln -s /etc/nginx/sites-available/solar_prescription /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   
   # Run app with gunicorn
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

---

## Environment Variables

For all platforms, set these:

**Required:**
- `NREL_API_KEY` - Your NREL API key
- `FLASK_ENV` - Set to `production` for live sites

**Optional:**
- `SECRET_KEY` - Flask secret key (auto-generated if not set)

---

## Performance Tips

1. **Use gunicorn** in production instead of Flask dev server
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Enable caching** for frequently used locations

3. **Add rate limiting** to prevent API abuse

4. **Use CDN** for static files

---

## Monitoring

### Free Monitoring Tools:
- **UptimeRobot**: Check if site is up
- **Google Analytics**: Track usage
- **Sentry**: Error tracking

### Add to app.py:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

---

## Custom Domain

After deployment:

1. **Buy domain** (Namecheap, Google Domains, etc.)

2. **Add DNS records**:
   - Type: A or CNAME
   - Points to: your-app-url

3. **Configure in platform**:
   - Render: Settings → Custom Domain
   - Heroku: Settings → Domains
   - Others: Check their docs

---

## Troubleshooting Deployment

### "Module not found"
- Ensure `requirements.txt` includes all dependencies
- Check Python version (3.8+)

### "API key error"
- Verify environment variable is set correctly
- No quotes around the value in environment config

### "Port already in use"
- Change port in app.py
- Or use environment variable: `PORT`

### "502 Bad Gateway"
- Check app is running
- Verify proxy settings in nginx/platform
- Check logs for errors

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Render | ✓ (750 hrs/month) | $7/month | Hobby projects |
| Heroku | ✓ (550 hrs/month) | $7/month | Quick deploys |
| PythonAnywhere | ✓ (Limited) | $5/month | Simple apps |
| DigitalOcean | ✓ ($200 credit) | $5/month+ | Scalable apps |
| AWS EC2 | ✓ (1 year) | $5/month+ | Full control |

**Recommendation**: Start with **Render** (easiest) or **PythonAnywhere** (most beginner-friendly)

---

## Next Steps After Deployment

1. Test all features thoroughly
2. Share with test users
3. Monitor error logs
4. Add analytics
5. Collect feedback
6. Iterate and improve

Good luck with your deployment! 🚀
