# National Grid Flask API

Simple Flask API to serve National Grid NYC Metro usage data.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Set environment variables:**
   ```bash
   export NATIONAL_GRID_USERNAME='your_username'
   export NATIONAL_GRID_PASSWORD='your_password'
   ```

3. **Run the Flask app:**
   ```bash
   cd app/
   python app.py
   ```

## API Endpoints

- **GET /** - API information
- **GET /health** - Health check
- **GET /usage** - Get National Grid usage and cost data

## Example Usage

```bash
# Health check
curl http://localhost:5000/health

# Get usage data
curl http://localhost:5000/usage
```

## Example Response

```json
{
  "success": true,
  "data": {
    "usage_over_time": [...],
    "cost_over_time": [...],
    "current_month_estimate": {...},
    "summary": {...}
  }
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NATIONAL_GRID_USERNAME` | Your National Grid account username |
| `NATIONAL_GRID_PASSWORD` | Your National Grid account password | 