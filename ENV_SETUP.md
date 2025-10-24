# Environment Variables Setup

This application uses environment variables to store sensitive information like passwords. This keeps credentials secure and prevents them from being committed to version control.

## Initial Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your actual passwords:**
   ```bash
   # The .env file is already gitignored and won't be committed
   nano .env  # or use your preferred editor
   ```

3. **Install dependencies:**
   ```bash
   pip install python-dotenv streamlit
   ```

## Environment Variables

The following variables are used in the application:

- `XRM_DEFAULT_PASSWORD` - Default password for XRM account resets
- `SPECTRA_DEFAULT_PASSWORD` - Default password for Spectra PM/Client accounts
- `DEFAULT_PASSWORD_SUFFIX` - Suffix used when generating employee passwords (e.g., #24)
- `AD_DISABLED_OU` - Active Directory OU path for disabled accounts
- `AD_HI_USER_PATH` - Active Directory path for Health Intelligence users

## Security Notes

- ✅ `.env` is listed in `.gitignore` and will NOT be committed to Git
- ✅ `.env.example` contains template without real passwords (safe to commit)
- ⚠️ Never commit actual passwords or the `.env` file to version control
- ⚠️ Keep your `.env` file secure and don't share it

## Verifying Setup

Test that environment variables load correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Setup OK' if os.getenv('XRM_DEFAULT_PASSWORD') else 'Missing .env file')"
```

If you see "Setup OK", you're ready to run the application!
