# National Grid NYC Metro

This is a simple script to get the monthly utility usage from National Grid for NYC Metro customers only.

```bash
# Install dependencies
pip install -r script/requirements.txt

# Install Playwright browser
playwright install chromium

# Run the script
python3 script/nationalgridmetro.py <username> <password>
```
Example response:
```json
{
  "usage_over_time": [
    {
      "period": "2023-01-15 to 2023-02-14",
      "usage_amount": 156.8,
      "usage_unit": "therms",
      "start_date": "2023-01-15",
      "end_date": "2023-02-14"
    },
    {
      "period": "2023-02-15 to 2023-03-14", 
      "usage_amount": 142.3,
      "usage_unit": "therms",
      "start_date": "2023-02-15",
      "end_date": "2023-03-14"
    },
    {
      "period": "2023-03-15 to 2023-04-14",
      "usage_amount": 98.7,
      "usage_unit": "therms",
      "start_date": "2023-03-15", 
      "end_date": "2023-04-14"
    },
    ...
  ],
  "cost_over_time": [
    {
      "period": "2023-01-15 to 2023-02-14",
      "cost_amount": 189.45,
      "currency": "USD",
      "start_date": "2023-01-15",
      "end_date": "2023-02-14"
    },
    {
      "period": "2023-02-15 to 2023-03-14",
      "cost_amount": 172.83,
      "currency": "USD", 
      "start_date": "2023-02-15",
      "end_date": "2023-03-14"
    },
    {
      "period": "2023-03-15 to 2023-04-14",
      "cost_amount": 123.67,
      "currency": "USD",
      "start_date": "2023-03-15",
      "end_date": "2023-04-14"
    },
    ...
  ],
  "current_month_estimate": {
    "period": "2024-01-15 to 2024-02-14",
    "estimated_usage": 145.2,
    "usage_unit": "therms",
    "estimated_cost": 181.67,
    "currency": "USD",
    "days_into_period": 18,
    "total_days_in_period": 31
  },
  "summary": {
    "total_periods": 12,
    "total_usage": 1139.7,
    "usage_unit": "therms",
    "total_cost": 1304.19,
    "currency": "USD",
    "average_monthly_usage": 94.98,
    "average_monthly_cost": 108.68,
    "highest_usage_period": "2023-12-15 to 2024-01-14",
    "highest_usage_amount": 167.9,
    "lowest_usage_period": "2023-07-15 to 2023-08-14", 
    "lowest_usage_amount": 16.8,
    "highest_cost_period": "2023-12-15 to 2024-01-14",
    "highest_cost_amount": 203.91,
    "lowest_cost_period": "2023-07-15 to 2023-08-14",
    "lowest_cost_amount": 45.23
  }
}
```