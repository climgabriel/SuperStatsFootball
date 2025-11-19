# APIFootball.com Migration Guide

## Overview

This document describes the migration from `api-sports.io` to `apifootball.com` (apiv3.apifootball.com).

## Key Differences

### 1. Authentication
- **OLD (api-sports.io)**: Header-based authentication
  ```python
  headers = {"x-apisports-key": "YOUR_KEY"}
  ```
- **NEW (apifootball.com)**: Query parameter authentication
  ```python
  params = {"APIkey": "YOUR_KEY"}
  ```

### 2. Endpoint Structure
- **OLD**: RESTful paths (`/leagues`, `/teams`, `/fixtures`)
- **NEW**: Action-based query parameters (`?action=get_leagues`, `?action=get_teams`)

### 3. Parameter Names
| Feature | OLD (api-sports.io) | NEW (apifootball.com) |
|---------|---------------------|----------------------|
| Fixture ID | `fixture` or `id` | `match_id` |
| League filter | `league` | `league_id` |
| Team filter | `team` | `team_id` |
| Date range | `from`/`to` | `from`/`to` (same) |
| Season | `season` | N/A (not required) |

### 4. Response Format
- **OLD**: Wrapped in `{"response": [...], "errors": {...}}`
- **NEW**: Direct array response or `{"error": "message"}` on error

## API Mapping

### Leagues
```python
# OLD
await client._make_request("leagues", {"season": 2023, "country": "England"})

# NEW
await client._make_request("get_leagues", {"country_id": 44})
```

### Teams
```python
# OLD
await client._make_request("teams", {"league": 39, "season": 2023})

# NEW
await client._make_request("get_teams", {"league_id": 152})
```

### Fixtures/Events
```python
# OLD
await client._make_request("fixtures", {
    "league": 39,
    "season": 2023,
    "from": "2024-01-01",
    "to": "2024-01-31"
})

# NEW
await client._make_request("get_events", {
    "league_id": 152,
    "from": "2024-01-01",
    "to": "2024-01-31"
})
```

### Statistics
```python
# OLD
await client._make_request("fixtures/statistics", {"fixture": 12345})

# NEW
await client._make_request("get_statistics", {"match_id": 12345})
```

### Standings
```python
# OLD
await client._make_request("standings", {"league": 39, "season": 2023})

# NEW
await client._make_request("get_standings", {"league_id": 152})
```

### Odds
```python
# OLD
await client._make_request("odds", {
    "fixture": 12345,
    "bookmaker": 8,  # Bet365
    "bet": 1  # Match Winner
})

# NEW
await client._make_request("get_odds", {
    "match_id": 12345
    # Note: apifootball.com returns odds from multiple bookmakers
})
```

### Predictions
```python
# OLD
Not available in api-sports.io free tier

# NEW
await client._make_request("get_predictions", {"match_id": 12345})
```

## New Features in apifootball.com

1. **Built-in Predictions**: AI/mathematical predictions with probabilities
2. **Head-to-Head**: Direct H2H history between teams
3. **Lineups**: Detailed lineup information
4. **Multiple Bookmaker Odds**: Single endpoint returns odds from many bookmakers

## Migration Checklist

- [x] Rewrite `app/services/apifootball.py` with new API structure
- [x] Update authentication from headers to query parameters
- [x] Map all endpoint names to action parameters
- [x] Test all API methods
- [ ] Update `app/services/data_sync_service.py` field mappings (if needed)
- [ ] Update database models if required
- [x] Remove old test scripts
- [x] Create new test script (`scripts/test_new_api.py`)

## Configuration

Update your `.env` file:
```env
APIFOOTBALL_BASE_URL=https://apiv3.apifootball.com/
APIFOOTBALL_API_KEY=your_api_key_here
```

## Testing

Run the test script to verify the API is working:
```bash
python scripts/test_new_api.py
```

## Known Limitations

1. **No Season Parameter**: apifootball.com doesn't require/use season parameters
2. **Different League IDs**: League IDs differ between the two APIs
3. **Rate Limits**: Check your plan's rate limits (may differ from api-sports.io)

## Support

- API Documentation: https://apifootball.com/documentation/
- Contact: support@apifootball.com
