# ML Predictions Architecture - Data Source Separation

## 🎯 **Critical Understanding**

**ML predictions are 100% independent from bookmaker odds.**

The system fetches bookmaker odds and ML predictions from **completely separate sources** and combines them only for display/comparison purposes.

---

## 📊 **Data Flow Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (SEPARATE)                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐     ┌──────────────────────────────┐
│   BOOKMAKER ODDS            │     │   YOUR DATABASE              │
│   (External API)            │     │   (Historical Matches)       │
│                             │     │                              │
│  API-Football/Superbet      │     │  ✓ Fixture table             │
│                             │     │  ✓ FixtureStat table         │
│  Odds: 1.90, 3.40, 4.20     │     │  ✓ TeamRating table          │
│                             │     │                              │
│  Stored in:                 │     │  Contains:                   │
│  └─ FixtureOdds table       │     │  └─ Match results            │
│                             │     │  └─ Goals scored/conceded    │
│                             │     │  └─ Team performance         │
│                             │     │  └─ Elo ratings              │
└──────────┬──────────────────┘     └──────────┬───────────────────┘
           │                                   │
           │                                   │
           │  NEVER INTERACT                   │
           │  ◄────────────►                   │
           │                                   │
           ▼                                   ▼
┌─────────────────────────────┐     ┌──────────────────────────────┐
│  Bookmaker Odds Display     │     │  ML Prediction Engine        │
│                             │     │                              │
│  - Pre-match odds           │     │  1. Calculate team stats     │
│  - Live odds                │     │     from historical data     │
│  - Over/Under               │     │                              │
│  - Halftime/Fulltime        │     │  2. Run ML models:           │
│                             │     │     • Poisson model          │
│                             │     │     • Dixon-Coles model      │
│                             │     │     • Elo rating model       │
│                             │     │                              │
│                             │     │  3. Calculate probabilities  │
│                             │     │     (e.g., 48.2%, 26.5%)     │
│                             │     │                              │
│                             │     │  4. Calculate consensus      │
└──────────┬──────────────────┘     └──────────┬───────────────────┘
           │                                   │
           │                                   │
           └──────────┬────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  Combined Response   │
           │                      │
           │  Both shown together │
           │  for comparison      │
           └──────────────────────┘
```

---

## 🔬 **How ML Predictions Work (Step-by-Step)**

### **Step 1: Calculate Team Statistics**
**Source:** `Fixture` table (YOUR database)

For each team, we analyze their last 10 matches:
```sql
SELECT * FROM fixtures
WHERE (home_team_id = ? OR away_team_id = ?)
  AND status IN ('FT', 'AET', 'PEN')
  AND season = ?
ORDER BY match_date DESC
LIMIT 10
```

**Extracted data:**
- Goals scored (e.g., 18 goals in 10 matches = 1.8 avg)
- Goals conceded (e.g., 12 goals in 10 matches = 1.2 avg)
- Attack strength = goals_scored / league_average
- Defense strength = goals_conceded / league_average

### **Step 2: Run Statistical Models**

#### **Poisson Model** (Free tier)
**Input:** Team attack/defense strengths from database
**Calculation:**
```python
home_expected_goals = home_attack_strength * away_defense_strength * home_advantage
away_expected_goals = away_attack_strength * home_defense_strength

# Calculate probability matrix
prob_matrix[home_goals, away_goals] = (
    poisson.pmf(home_goals, home_expected_goals) *
    poisson.pmf(away_goals, away_expected_goals)
)

# Sum probabilities for win/draw/loss
home_win_prob = sum of probabilities where home_goals > away_goals
draw_prob = sum of probabilities where home_goals == away_goals
away_win_prob = sum of probabilities where home_goals < away_goals
```

**NO odds involved!** Pure statistics from goal-scoring patterns.

#### **Dixon-Coles Model** (Starter+ tier)
**Input:** Same team stats + correlation factor
**Enhancement:** Adjusts for low-scoring games (0-0, 1-0, 0-1, 1-1)

```python
# Add correlation adjustment for low scores
if home_goals <= 1 and away_goals <= 1:
    tau_factor = correlation_adjustment(home_goals, away_goals)
    probability *= tau_factor
```

**NO odds involved!** Enhanced Poisson with correlation.

#### **Elo Rating Model** (Pro+ tier)
**Source:** `TeamRating` table (YOUR database)

```sql
SELECT elo_rating FROM team_ratings
WHERE team_id = ? AND league_id = ? AND season = ?
```

**Calculation:**
```python
# Elo ratings updated after each match result
expected_score = 1 / (1 + 10^((rating_b - rating_a) / 400))

# Convert to win/draw/loss probabilities
home_win_prob = expected_score * (1 - draw_factor)
draw_prob = draw_factor
away_win_prob = (1 - expected_score) * (1 - draw_factor)
```

**NO odds involved!** Based on historical win/loss records.

### **Step 3: Calculate Consensus**
Average the probabilities from all models available to the user's tier:

```python
home_win_consensus = average([poisson_home, dixon_coles_home, elo_home])
draw_consensus = average([poisson_draw, dixon_coles_draw, elo_draw])
away_win_consensus = average([poisson_away, dixon_coles_away, elo_away])
```

### **Step 4: Calculate True Odds**
Convert ML probabilities to implied odds:

```python
true_odd = 1.0 / probability

# Example:
# If ML says 48.2% home win probability
# True odd = 1 / 0.482 = 2.07
```

---

## 📋 **Code Flow (Actual Implementation)**

### **File:** `backend/app/services/prediction_pipeline.py`

```python
def generate_prediction(self, fixture_id: int, user_tier: str):
    # 1. Get fixture from database
    fixture = self.db.query(Fixture).filter(Fixture.id == fixture_id).first()

    # 2. Calculate team stats from HISTORICAL MATCHES ONLY
    home_stats = self.calculate_team_stats(
        team_id=fixture.home_team_id,
        league_id=fixture.league_id,
        season=fixture.season
    )
    # Returns: {
    #   "goals_scored": 1.8,
    #   "goals_conceded": 1.2,
    #   "attack_strength": 1.2,
    #   "defense_strength": 0.85
    # }

    away_stats = self.calculate_team_stats(
        team_id=fixture.away_team_id,
        league_id=fixture.league_id,
        season=fixture.season
    )

    # 3. Run ML models with stats (NO ODDS DATA!)
    predictions = {}

    if "poisson" in available_models:
        predictions["poisson"] = self.poisson.predict(
            home_attack=home_stats["attack_strength"],
            home_defense=home_stats["defense_strength"],
            away_attack=away_stats["attack_strength"],
            away_defense=away_stats["defense_strength"]
        )
        # Returns: {"probabilities": {"home_win": 0.482, "draw": 0.265, "away_win": 0.253}}

    if "dixon_coles" in available_models:
        predictions["dixon_coles"] = self.dixon_coles.predict(...)
        # Same input as Poisson, different calculation

    if "elo" in available_models:
        home_rating = self._get_team_rating(...)  # From TeamRating table
        away_rating = self._get_team_rating(...)  # From TeamRating table
        predictions["elo"] = self.elo.predict(home_rating, away_rating)

    # 4. Calculate consensus from all models
    consensus = self._calculate_consensus(predictions)
    # Returns: {"home_win": 45.5, "draw": 28.3, "away_win": 26.2}  # percentages

    return {
        "predictions": predictions,
        "consensus": consensus,
        "models_used": available_models
    }
```

### **File:** `backend/app/routers/combined_predictions.py`

```python
@router.get("/fixtures/predictions-with-odds")
async def get_fixtures_with_predictions_and_odds(...):
    for fixture in fixtures:
        # ========================================
        # STEP 1: Get bookmaker odds (EXTERNAL)
        # ========================================
        odds_obj = fixture.odds  # From FixtureOdds table (API-Football data)

        # ========================================
        # STEP 2: Generate ML predictions (DATABASE ONLY)
        # ========================================
        prediction_data = prediction_pipeline.generate_prediction(
            fixture_id=fixture.id,
            user_tier=current_user.tier
        )
        # This calls the code above - ZERO odds input!

        # ========================================
        # STEP 3: Combine in response (for comparison)
        # ========================================
        return {
            "bookmaker_odds": {
                "1": odds_obj.home_win_odds,  # From Superbet
                "X": odds_obj.draw_odds,
                "2": odds_obj.away_win_odds
            },
            "ml_probability": {
                "1": f"{home_prob_pct}%",  # From YOUR ML models
                "X": f"{draw_prob_pct}%",
                "2": f"{away_prob_pct}%"
            },
            "ml_true_odds": {
                "1": 1 / home_prob,  # Calculated from ML probability
                "X": 1 / draw_prob,
                "2": 1 / away_prob
            }
        }
```

---

## ✅ **Verification Checklist**

To confirm ML predictions are independent from odds:

1. **Check database queries:**
   - `prediction_pipeline.py` only queries `Fixture`, `FixtureStat`, `TeamRating` tables
   - ❌ NEVER queries `FixtureOdds` table

2. **Check model inputs:**
   - Poisson: attack_strength, defense_strength (from historical goals)
   - Dixon-Coles: Same as Poisson + correlation factor
   - Elo: team ratings (from win/loss history)
   - ❌ NONE of them accept odds as input

3. **Check calculation methods:**
   - All use statistical formulas (Poisson distribution, Elo formula)
   - ❌ NO odds data in any calculation

4. **Check data flow:**
   - Odds fetched: `fixture.odds` → from `FixtureOdds` table
   - Predictions calculated: `prediction_pipeline.generate_prediction()` → from `Fixture` stats
   - Combined: Only in the final response for user display

---

## 🎯 **Summary**

**BOOKMAKER ODDS:**
- Source: API-Football/Superbet API
- Storage: `FixtureOdds` table
- Usage: Display only
- Not used in calculations

**ML PREDICTIONS:**
- Source: YOUR database (`Fixture`, `FixtureStat`, `TeamRating` tables)
- Calculation: Statistical models (Poisson, Dixon-Coles, Elo)
- Input: Historical match results, goals, team performance
- Output: Probabilities based on past data
- **NEVER uses bookmaker odds**

**COMBINED RESPONSE:**
- Shows both side-by-side for comparison
- Users can see if ML predictions differ from bookmaker odds
- Identifies value betting opportunities
- But the two sources are completely independent

---

## 🔧 **How to Verify in Production**

1. **Disable odds fetching temporarily:**
   ```python
   # Comment out odds fetch
   # odds_obj = fixture.odds
   odds_obj = None
   ```

2. **Run ML predictions:**
   - They will still work perfectly
   - Probabilities will still be calculated
   - True odds will still be generated

3. **This proves:** ML predictions don't need odds data at all!

---

**Last Updated:** November 16, 2025
**Author:** Claude AI
**Purpose:** Clarify ML prediction data sources for SuperStatsFootball
