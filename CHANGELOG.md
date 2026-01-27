# Changelog - MenuPilot

## [1.1.0] - 2026-01-26

### ✨ New Features

#### PDF Support
- **Menu PDFs**: Now accepts PDF files in addition to images (JPG, PNG, WEBP)
- **Automatic Conversion**: PDFs are automatically converted to images using PyMuPDF (with pdf2image fallback)
- **Frontend Support**: Upload dropzone now accepts PDF files
- **Backend Processing**: `menu_extractor.py` handles PDF conversion transparently

#### API Key Management
- **Setup Script**: New `scripts/setup_api_key.sh` for easy API key configuration
- **Makefile Command**: `make setup-apikey` for interactive setup
- **Better Documentation**: Clear instructions in QUICK_START.md

### 🔧 Improvements

#### Developer Experience
- **Makefile**: Added comprehensive commands for setup, run, test, lint
- **Quick Start Guide**: New QUICK_START.md with step-by-step instructions
- **API Key Script**: Interactive script for configuring Gemini API key
- **Better Error Messages**: Clear guidance when API key is missing

#### Testing & Quality
- **Unit Tests**: Basic API endpoint tests in `backend/tests/`
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing
- **Test Configuration**: pytest.ini with proper async support
- **Dev Dependencies**: `requirements-dev.txt` for testing tools

#### Documentation
- **Updated README**: Added PDF support, Makefile commands, troubleshooting
- **Quick Start**: Dedicated guide for new users
- **Changelog**: This file to track changes
- **API Key Setup**: Clear instructions for configuration

### 📦 Dependencies Added

```
pdf2image==1.17.0      # PDF to image conversion
PyMuPDF==1.24.0        # Fast PDF processing
pytest>=8.0.0          # Testing framework
pytest-asyncio>=0.23.0 # Async test support
ruff>=0.3.0            # Linting
```

### 🐛 Bug Fixes

- **API Key Error**: Added clear error messages and setup instructions
- **PDF Upload**: Frontend now properly accepts PDF files
- **File Validation**: Backend validates PDF extensions correctly

### 📝 Files Added

```
.github/workflows/ci.yml          # CI/CD pipeline
Makefile                          # Development commands
QUICK_START.md                    # Quick start guide
CHANGELOG.md                      # This file
backend/requirements-dev.txt      # Dev dependencies
backend/pytest.ini                # Test configuration
backend/tests/__init__.py         # Test package
backend/tests/conftest.py         # Test fixtures
backend/tests/test_api.py         # API tests
scripts/setup_api_key.sh          # API key setup script
```

### 📝 Files Modified

```
README.md                         # Updated with PDF support, Makefile
backend/requirements.txt          # Added PDF libraries
backend/app/config.py             # Added PDF to allowed extensions
backend/app/services/menu_extractor.py  # PDF conversion support
backend/.env.example              # Emphasized API key requirement
frontend/src/components/FileUpload.tsx  # PDF upload support
```

### 🚀 Usage Examples

#### Setup with Makefile
```bash
make setup              # Install all dependencies
make setup-apikey       # Configure API key
make run                # Start backend + frontend
```

#### Upload PDF Menu
```bash
# Frontend: Drag & drop PDF file in menu upload area
# Backend automatically converts PDF to image and processes
```

#### Run Tests
```bash
make test               # Run all tests
make lint               # Check code quality
```

### 🔜 Future Improvements

- [ ] Multi-page PDF support
- [ ] Redis for session storage (currently in-memory)
- [ ] More comprehensive test coverage
- [ ] Integration tests with Gemini API
- [ ] Performance monitoring with Prometheus
- [ ] JWT authentication for production

### 📚 Documentation Links

- [Quick Start Guide](QUICK_START.md)
- [Full README](README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)

---

## [1.0.0] - 2026-01-25

### Initial Release

- Menu extraction from images (OCR + Gemini multimodal)
- BCG Matrix classification
- Sales prediction (XGBoost + Neural Networks)
- Campaign generation
- Thought signatures with multiple levels
- Verification agent (Vibe Engineering)
- Pipeline orchestrator (Marathon Agent)
- Next.js frontend with TailwindCSS
- FastAPI backend
- Docker support
