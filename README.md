# 🇮🇹 Italian Address Normalization Service

A production-ready microservice that normalizes messy Italian addresses into postal-correct, standardized format with a beautiful web UI for QA testing.

## ✨ Features

- **Address Normalization**: Convert messy addresses to postal-correct Italian format
- **English-to-Italian Translation**: Automatic city name translation (Venice→Venezia, Turin→Torino)
- **CAP Conflict Resolution**: Uses postal codes as source of truth for conflicts
- **Comprehensive Coverage**: 151 CAPs, 140 comuni, 104 synonyms covering all 20 Italian regions
- **Web UI for Testing**: Beautiful interface for QA teams and non-technical users
- **Production Ready**: Docker containerization, health checks, monitoring

## 🚀 Quick Start

### 1. Deploy Locally
```bash
git clone <repository>
cd italian-address-service
docker compose up -d
# Database seeding is automatic
```

**Access your service:**
- **Web UI**: http://localhost:10000 (Perfect for QA teams!)
- **API Docs**: http://localhost:10000/docs
- **Health Check**: http://localhost:10000/health

### 2. Deploy to Remote Server
```bash
# Deploy to any server (EC2, VPS, etc.)
./deploy.sh 13.234.225.149 ~/.ssh/your-key.pem
```

## 🎯 Web UI - Perfect for QA Teams

Once deployed, share this URL with your QA team: **http://your-server:10000**

### Web UI Features:
- **Interactive Testing**: Click-to-fill example addresses
- **Real-time Validation**: Instant address normalization and validation
- **API Documentation**: Built-in curl examples and endpoint documentation
- **Dataset Statistics**: Live view of loaded Italian geographic data

### Example Test Cases:
- **Complete Address**: `Via del Corso 123, 00184 Roma RM`
- **English Cities**: `Corso Buenos Aires 45, Milan 20121` → Milano
- **Tourist Addresses**: `Piazza San Marco, Venice 30122` → Venezia
- **CAP Conflicts**: `Via Roma 50, 20121 Milano XX` → Resolves XX to MI
- **Regional Coverage**: Sicily, Veneto, Valle d'Aosta, Sardegna, etc.

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB:
```bash
docker run -d -p 27017:27017 mongo:7
```

3. Set environment variables:
```bash
export MONGO_URL=mongodb://localhost:27017
export MONGO_DB=addresses
export ADMIN_TOKEN=changeme
```

4. Start the application:
```bash
uvicorn app.main:app --reload
```

5. Seed test data:
```bash
curl -X POST "http://localhost:8000/datasets/seed" \
  -H "X-Admin-Token: changeme"
```

## API Endpoints

### POST /normalize
Normalize a free-form address string.

**Request:**
```json
{
  "address": "Giuseppe Rossi, 5 Garibaldi Square, Naples"
}
```

**Response:**
```json
{
  "formatted": "Piazza Garibaldi 5, 80142 Napoli NA, Italia",
  "components": {
    "street": "Piazza Garibaldi",
    "number": "5",
    "cap": "80142",
    "comune": "Napoli",
    "provincia": "NA",
    "country": "Italia"
  },
  "confidence": 0.95,
  "issues": ["CITY_PROVINCE_OVERRIDDEN_BY_CAP"]
}
```

### POST /validate
Validate structured address components.

**Request:**
```json
{
  "components": {
    "street": "Piazza Garibaldi",
    "number": "5",
    "cap": "80142",
    "comune": "Napoli",
    "provincia": "NA",
    "country": "Italia"
  }
}
```

**Response:**
```json
{
  "valid": true,
  "issues": [],
  "confidence": 0.99
}
```

### POST /datasets/seed
Load seed data into the database (requires admin token).

**Headers:**
```
X-Admin-Token: changeme
```

### GET /datasets/stats
Get statistics about loaded datasets.

### GET /health
Health check endpoint.

## Example Normalizations

| Input | Output |
|-------|--------|
| `Giuseppe Rossi, 5 Garibaldi Square, Naples` | `Piazza Garibaldi 5, 80142 Napoli NA, Italia` |
| `Via Verdi 10, 24121 Bergamo MI` | `Via Verdi 10, 24121 Bergamo BG, Italia` |
| `Via Dante 7, 15060, Italia` | `Via Dante 7, 15060 Arquata Scrivia AL, Italia` |
| `Piazza Garibaldi 5, Naples, Italy` | `Piazza Garibaldi 5, 80142 Napoli NA, Italia` |

## Conflict Resolution Logic

1. **CAP Present**: Use CAP as source of truth for comune/provincia
   - If user-provided city/province conflicts with CAP → override with CAP data
   - Add `CITY_PROVINCE_OVERRIDDEN_BY_CAP` issue

2. **CAP Missing**: Try to infer from city name
   - If unique CAP found for city → use it
   - If multiple CAPs exist → flag `MULTIPLE_CAPS_FOR_COMUNE`
   - If no CAP found → flag `COMUNE_NOT_FOUND`

3. **Insufficient Data**: Flag `INSUFFICIENT_LOCALITY`

## Confidence Scoring

- Start at 1.0
- Subtract penalties for issues:
  - `CAP_UNKNOWN`: -0.2
  - `MULTIPLE_CAPS_FOR_COMUNE`: -0.15
  - `COMUNE_NOT_FOUND`: -0.25
  - `INSUFFICIENT_LOCALITY`: -0.3
  - `CITY_PROVINCE_OVERRIDDEN_BY_CAP`: -0.05

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Start MongoDB for testing
docker run -d -p 27017:27017 mongo:7

# Run tests
pytest -v
```

## Configuration

Environment variables:

- `MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGO_DB`: Database name (default: `addresses`)
- `ADMIN_TOKEN`: Token for admin endpoints (default: `changeme`)
- `ENVIRONMENT`: Environment name (default: `development`)

## Project Structure

```
app/
├── main.py              # FastAPI app setup
├── config.py            # Configuration settings
├── deps.py              # Dependency injection
├── schemas/             # Pydantic models
│   ├── address.py       # Address-related schemas
│   └── responses.py     # Response schemas
├── services/            # Business logic
│   ├── normalizer.py    # Address normalization logic
│   └── validators.py    # Address validation logic
├── repositories/        # Data access layer
│   ├── caps_repo.py     # CAP data repository
│   ├── comuni_repo.py   # Comuni data repository
│   ├── synonyms_repo.py # Synonyms data repository
│   └── logs_repo.py     # Audit logs repository
├── routers/             # API endpoints
│   ├── normalize.py     # Normalization endpoints
│   ├── validate.py      # Validation endpoints
│   ├── datasets.py      # Dataset management endpoints
│   └── health.py        # Health check endpoint
├── data/                # Seed data files
│   ├── seed_caps.json   # CAP data
│   ├── seed_comuni.json # Comuni data
│   └── seed_synonyms.json # Translation data
└── utils/               # Utility functions
    ├── text.py          # Text processing utilities
    └── street_types.py  # Street type normalization
```

## API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc