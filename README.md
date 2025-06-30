# Amazon Title Generator - Streamlit App

A web application that generates compelling Amazon product titles using Few-Shot Learning (FSL) with GPT-4.

## Features

- 🎯 **Single Title Generation**: Generate titles for individual products
- 📊 **Batch Processing**: Process multiple products from Excel files
- 💰 **Cost Tracking**: Monitor API usage and costs
- 🎨 **User-Friendly Interface**: Clean Streamlit web interface
- 📈 **Amazon SEO Optimized**: Follows Amazon's title guidelines

## Technology Stack

- **AI Model**: OpenAI GPT-4o-mini
- **Learning Method**: Few-Shot Learning (FSL)
- **Web Framework**: Streamlit
- **Template Engine**: Jinja2
- **Data Processing**: Pandas
- **File Handling**: OpenPyXL

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in your project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Open Browser
Navigate to `http://localhost:8501`

## Troubleshooting Connection Issues

### Common Issues and Solutions

1. **"OpenAI API key not found"**
   - Create a `.env` file with your API key
   - Or set environment variable: `export OPENAI_API_KEY=your_key`

2. **"Failed to connect to OpenAI API"**
   - Check your API key is correct
   - Ensure you have sufficient credits
   - Test connection using: `python test_connection.py`

3. **Streamlit Runtime Warnings**
   - These warnings are normal when importing outside Streamlit context
   - They don't affect the app functionality

4. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version (3.9+ required)

### Test Your Setup
```bash
python test_connection.py
```

## Usage

### Single Title Generation
1. Go to "Single Title" tab
2. Enter original title (optional)
3. Enter product description
4. Click "Generate Title"
5. View results and cost analysis

### Batch Processing
1. Go to "Batch Processing" tab
2. Upload Excel file with columns:
   - `Title` (optional): Original titles
   - `Bullet Points`: Product descriptions
3. Click "Process All Titles"
4. Download results as Excel file

## Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set environment variables
5. Deploy

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Docker
```bash
docker build -t amazon-title-generator .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key amazon-title-generator
```

## File Structure
```
Amazon_Title_GenAI/
├── app.py                 # Main Streamlit application
├── title_FSL.py          # Original script (reference)
├── test_connection.py    # Connection test script
├── requirements.txt      # Python dependencies
├── .streamlit/           # Streamlit configuration
│   └── config.toml
├── README.md            # This file
├── data/                # Sample data files
└── output/              # Generated results
```

## API Guidelines

The title generation follows Amazon-specific guidelines:
- **Length**: Under 200 characters
- **Keywords**: Critical keywords in first 80 characters
- **Branding**: Avoid brand name conflicts
- **Specificity**: Include shape and pack details
- **Uniqueness**: Avoid synonym repetition

## Cost Optimization

Using GPT-4o-mini for cost efficiency:
- Input: $0.06 per 1M tokens
- Output: $2.40 per 1M tokens

## Support

For issues:
1. Run `python test_connection.py` to diagnose problems
2. Check the "About" tab in the app
3. Review error messages in the terminal
4. Ensure all dependencies are installed
