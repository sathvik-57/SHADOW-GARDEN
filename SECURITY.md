# Security Policy

## Project Overview

**Shadow Garden** is an IoT-based smart agriculture system consisting of:
- **ESP32 Microcontrollers** — Sensor data collection & relay control
- **FastAPI Backend** — REST API, ML inference, and SQLite database
- **React Frontend** — Dashboard and monitoring UI

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Email**: Contact the maintainer at [sathvik-57](https://github.com/sathvik-57) via GitHub
2. **Do NOT** open a public issue for security vulnerabilities
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgement**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix/Resolution**: Targeted within 30 days depending on severity

## Security Best Practices

This project follows these security measures:

### Backend
- CORS middleware is configured to restrict cross-origin requests
- Environment variables (`.env`) are used for sensitive credentials and are excluded from version control
- SQLite databases are listed in `.gitignore` to prevent data leaks
- Input validation is handled via Pydantic models

### ML / AI Models
- Model weights (`.pt`, `.pth`, `.pkl`, `.h5`) are excluded from version control via `.gitignore`
- Uploaded images for disease detection are validated for file type and size before inference
- ML inference runs server-side only; no model files are exposed to the client
- Training datasets containing sensitive or large data are gitignored under `DATASET/`
- Model outputs (crop recommendations, disease predictions) are treated as advisory and should not be used as sole decision-making inputs without human review

### IoT / ESP32
- Wi-Fi credentials and API keys are hardcoded only for development; use environment-based configuration for production
- HTTPS is recommended for all API communication between ESP32 and the backend

### Frontend
- No sensitive keys or tokens are stored in client-side code
- API base URLs are configured via environment variables

### General
- ML model weights and checkpoints are excluded from version control
- All secrets and `.env` files are in `.gitignore`

## Disclaimer

This project is developed as an academic/educational IoT project (4th Semester). It is not intended for production-grade deployment without further security hardening.
