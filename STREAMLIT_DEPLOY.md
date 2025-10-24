# Deploying to Streamlit Cloud

This guide helps you deploy the Employee Management Toolkit to Streamlit Cloud for easy online access.

## Step 1: Push to GitHub

Make sure your code is pushed to GitHub (already done ✅).

## Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - **Repository**: `kojosbk/Serverless-Movies-API`
   - **Branch**: `main`
   - **Main file path**: `login_details_app.py`

## Step 3: Configure Secrets

**IMPORTANT**: You must add the passwords as secrets in Streamlit Cloud.

1. In your Streamlit Cloud app dashboard, click on **"⚙️ Settings"**
2. Go to the **"Secrets"** section
3. Copy and paste the following into the secrets editor:

```toml
XRM_DEFAULT_PASSWORD = "Inhealth1020"
SPECTRA_DEFAULT_PASSWORD = "Blue1957"
DEFAULT_PASSWORD_SUFFIX = "#24"
AD_DISABLED_OU = "OU=Disabled to Delete,OU=IHGD HouseKeeping,OU=IHGD Internal,DC=ihgd,DC=inhealthgroup,DC=com"
AD_HI_USER_PATH = "OU=AHW DESP,OU=HIUsers,DC=hi,DC=int"
```

4. Click **"Save"**

## Step 4: Deploy

Click **"Deploy"** and wait for the app to start.

## How It Works

The app is configured to work in two environments:

### Local Development
- Uses `.env` file (gitignored, stays on your machine)
- Run with: `streamlit run login_details_app.py`

### Streamlit Cloud
- Uses Streamlit Secrets (configured in cloud dashboard)
- Secrets are encrypted and never exposed in the repository
- The app automatically detects which environment it's in

## Security Notes

✅ Passwords are stored securely in Streamlit Cloud secrets
✅ Secrets are encrypted and not visible in logs
✅ The `.env` file is never committed to Git
✅ `.streamlit/secrets.toml` is also gitignored (local development only)

## Troubleshooting

**Error: "ModuleNotFoundError: No module named 'dotenv'"**
- Make sure `requirements.txt` is in the repository root
- Redeploy the app from Streamlit Cloud dashboard

**Error: "KeyError" for passwords**
- Make sure you've added all secrets in the Streamlit Cloud dashboard
- Check that secret names match exactly (case-sensitive)

**App not updating**
- Click "Reboot app" in the Streamlit Cloud dashboard
- Or push a new commit to trigger redeployment

## Access Control

Since this app contains sensitive HR tools, consider:
- Using Streamlit Cloud's password protection feature
- Sharing the app URL only with authorized personnel
- Upgrading to Streamlit Cloud Teams for SSO/authentication

## Support

For issues with:
- **Streamlit Cloud**: [Streamlit Community Forums](https://discuss.streamlit.io/)
- **This app**: Contact your IT/HR team
