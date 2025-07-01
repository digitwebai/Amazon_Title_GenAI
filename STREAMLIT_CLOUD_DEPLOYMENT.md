# Streamlit Cloud Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository
Make sure your code is pushed to GitHub with these files:
- `app.py` (main application)
- `requirements.txt` (dependencies)
- `.gitignore` (excludes sensitive files)
- `.streamlit/config.toml` (configuration)

### 2. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure your app**:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a unique URL (optional)

### 3. Set Environment Variables

**CRITICAL**: You must set the OpenAI API key in Streamlit Cloud:

1. In your app settings, go to **"Secrets"** section
2. Add this configuration:
```toml
[openai]
api_key = "your_actual_openai_api_key_here"
```

**OR** use environment variables:
- Go to **"Advanced settings"**
- Add environment variable: `OPENAI_API_KEY`
- Set value to your actual OpenAI API key

### 4. Deploy
Click **"Deploy"** and wait for the build to complete.

## 🔧 Troubleshooting Common Issues

### Issue 1: "OpenAI API key not found"
**Solution**: 
- Set the API key in Streamlit Cloud secrets or environment variables
- Make sure you're using the correct API key format

### Issue 2: "Module not found" errors
**Solution**:
- Check that all dependencies are in `requirements.txt`
- Ensure package versions are compatible
- Try using `>=` instead of `==` for version numbers

### Issue 3: Build fails
**Solution**:
- Check the build logs in Streamlit Cloud
- Ensure `app.py` is in the root directory
- Verify all imports are correct

### Issue 4: App loads but doesn't work
**Solution**:
- Check the app logs in Streamlit Cloud
- Verify environment variables are set correctly
- Test the API key locally first

## 📁 Required File Structure

```
your-repo/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── .streamlit/
│   └── config.toml       # Streamlit config
├── data/                 # Sample data (optional)
└── README.md             # Documentation
```

## 🔒 Security Best Practices

1. **Never commit API keys** to your repository
2. **Use Streamlit secrets** for sensitive data
3. **Set up proper .gitignore** to exclude sensitive files
4. **Use environment variables** in production

## 📊 Monitoring Your App

- **App URL**: Your app will be available at `https://your-app-name.streamlit.app`
- **Logs**: Check logs in Streamlit Cloud dashboard
- **Usage**: Monitor API usage and costs in OpenAI dashboard

## 🆘 Getting Help

If you're still having issues:

1. **Check Streamlit Cloud logs** for error messages
2. **Test locally first** with `streamlit run app.py`
3. **Verify your API key** works with a simple test
4. **Check Streamlit documentation** at [docs.streamlit.io](https://docs.streamlit.io)

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] `app.py` is the main file
- [ ] `requirements.txt` contains all dependencies
- [ ] `.gitignore` excludes sensitive files
- [ ] OpenAI API key set in Streamlit Cloud
- [ ] App builds successfully
- [ ] App loads without errors
- [ ] API calls work correctly 