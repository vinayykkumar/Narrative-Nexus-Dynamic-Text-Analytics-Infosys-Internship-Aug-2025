# AI Narrative Nexus Backend

A powerful Python-based FastAPI backend for advanced text preprocessing and analytics.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd backend
chmod +x start_backend.sh
./start_backend.sh
```

### Option 2: Manual Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python3 -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords') 
nltk.download('wordnet')
nltk.download('omw-1.4')
"

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 8GB RAM recommended for large datasets
- 1GB free disk space

## 🔧 Configuration

Create a `.env` file in the backend directory:

```bash
# Application settings
APP_NAME="AI Narrative Nexus Backend"
DEBUG=false
PORT=8000

# Processing settings
DEFAULT_REMOVE_STOPWORDS=true
DEFAULT_USE_STEMMING=true
BATCH_SIZE=1000

# Security (change in production)
SECRET_KEY=your-secret-key-here
```

## 🌐 API Endpoints

Once running, access:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key Endpoints
- `POST /preprocess/text` - Single text preprocessing
- `POST /preprocess/batch` - Batch text processing
- `POST /preprocess/file` - File upload processing
- `POST /preprocess/job/{id}` - Background job processing

## 📁 File Structure

```
backend/
├── app.py                    # Main FastAPI application
├── preprocessing_service.py  # Enhanced preprocessing engine
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── start_backend.sh        # Automated setup script
├── .env                    # Environment variables
└── venv/                   # Virtual environment (created on setup)
```

## 🔍 Features

### Advanced Text Processing
- ✅ NLTK-powered tokenization
- ✅ Porter stemming algorithm  
- ✅ WordNet lemmatization
- ✅ Comprehensive URL/email removal
- ✅ Social media cleanup (@mentions, #hashtags)
- ✅ Smart number and punctuation handling
- ✅ Contraction expansion

### Performance Features
- ✅ Async processing
- ✅ Batch operations
- ✅ Background jobs for large datasets
- ✅ File upload support (TXT, CSV, JSON)
- ✅ Real-time progress tracking
- ✅ Comprehensive error handling

### Analytics & Statistics
- ✅ Processing time metrics
- ✅ Compression ratio analysis
- ✅ Token and vocabulary statistics
- ✅ Removal statistics (URLs, emails, etc.)
- ✅ Batch summary analytics

## 🧪 Testing

Test the backend with curl:

```bash
# Health check
curl http://localhost:8000/health

# Single text processing
curl -X POST "http://localhost:8000/preprocess/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world! Check out https://example.com"}'

# Batch processing
curl -X POST "http://localhost:8000/preprocess/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Text 1", "Text 2", "Text 3"]}'
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check if port is in use
netstat -tulpn | grep :8000

# Try different port
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

**NLTK errors:**
```bash
# Manually download NLTK data
python3 -c "
import nltk
nltk.download('all')
"
```

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Performance

### Benchmarks
| Operation | Time | Memory |
|-----------|------|--------|
| Single text (1KB) | ~15ms | <2MB |
| Batch (100 texts) | ~500ms | <10MB |
| File upload (1MB) | ~2s | <50MB |

### Optimization Tips
- Use batch processing for multiple texts
- Enable background jobs for large datasets
- Adjust batch_size in config for your hardware
- Monitor memory usage with large files

## 🔒 Security

### Production Deployment
```bash
# Update .env for production
DEBUG=false
SECRET_KEY=strong-random-key-here

# Use production ASGI server
pip install gunicorn
gunicorn app:app -k uvicorn.workers.UvicornWorker
```

### CORS Configuration
Update `allowed_origins` in `config.py` for your domain:
```python
allowed_origins = [
    "http://localhost:3000",
    "https://your-domain.com"
]
```

## 📈 Monitoring

### Health Monitoring
```bash
# Check backend status
curl http://localhost:8000/health

# Monitor logs
tail -f backend.log
```

### Performance Monitoring
- Processing time metrics in API responses
- Memory usage tracking
- Error rate monitoring
- Request statistics

## 🤝 Integration

### Frontend Integration
The backend automatically integrates with the Next.js frontend via the API client at `lib/api/backend-client.ts`.

### External Integration
```python
import requests

# Single text processing
response = requests.post(
    "http://localhost:8000/preprocess/text",
    json={"text": "Your text here"}
)
result = response.json()
```

## 🔄 Updates

### Updating Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Update packages
pip install --upgrade -r requirements.txt

# Update NLTK data
python3 -c "import nltk; nltk.download('all')"
```

### Configuration Updates
Modify `.env` file and restart the server:
```bash
# Kill existing server (Ctrl+C)
# Start with new configuration
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Documentation

- **Full Documentation**: `../BACKEND_PREPROCESSING_DOCUMENTATION.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Frontend Integration**: `../lib/api/backend-client.ts`

## 🆘 Support

For issues:
1. Check the logs: `tail -f backend.log`
2. Verify configuration: Review `.env` and `config.py`
3. Test with curl commands above
4. Check Python and dependency versions
5. Review the full documentation

---

**Ready to process text at scale! 🚀**
