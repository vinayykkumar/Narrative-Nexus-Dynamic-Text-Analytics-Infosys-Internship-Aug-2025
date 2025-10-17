# Data Analysis Dashboard

A powerful data analysis tool with an elegant frontend that provides visualization, sentiment analysis, insights, and PDF export capabilities.

## Features

- **File Upload**: Support for multiple file formats (CSV, TSV, PDF, TXT, Excel)
- **Interactive Visualizations**: Animated word clouds, plots, and matrices
- **Sentiment Analysis**: Detailed sentiment breakdown with visualizations
- **Insights**: AI-generated insights and topic modeling
- **PDF Export**: Generate comprehensive reports for sharing

## Requirements

- Python 3.7+
- Flask
- Pandas
- NumPy
- Matplotlib
- Seaborn
- NLTK
- Scikit-learn
- WordCloud
- Sumy
- Google Gemini API

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/data-analysis-dashboard.git
   cd data-analysis-dashboard
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key:
   - Create a `.env` file in the project root
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

## Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Upload a file and explore the analysis features

## Usage Guide

1. **Landing Page**: Upload your data file (CSV, TSV, PDF, TXT, Excel)
2. **Visualization**: View generated plots and word clouds
3. **Sentiment Analysis**: Explore sentiment distribution and related visualizations
4. **Insights**: Review AI-generated insights and topic modeling results
5. **Export**: Generate PDF reports of your analysis

## Project Structure

```
data-analysis-dashboard/
├── app.py                 # Flask application
├── main.py                # Backend analysis logic
├── requirements.txt       # Project dependencies
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── plots/             # Generated visualizations
├── templates/             # HTML templates
│   ├── landing.html       # Landing page
│   ├── visualization.html # Visualization page
│   ├── sentiment.html     # Sentiment analysis page
│   ├── insights.html      # Insights page
│   └── export-pdf.html    # PDF export page
└── uploads/               # Uploaded files directory
```

## Customization

- Modify `main.py` to add new analysis techniques
- Edit templates in the `templates/` directory to customize the UI
- Add new visualizations by extending the plotting functions

## Troubleshooting

- **File Upload Issues**: Ensure the `uploads/` directory exists and has write permissions
- **Visualization Errors**: Check that all required Python packages are installed
- **PDF Export Problems**: Verify that html2pdf.js is properly loaded

## License

This project is licensed under the MIT License - see the LICENSE file for details.