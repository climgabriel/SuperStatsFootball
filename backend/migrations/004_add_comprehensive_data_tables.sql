-- Migration: Add comprehensive data tables (standings, lineups, top scorers, predictions, h2h)
-- Date: 2025-11-19

-- Table: standings (league table/standings)
CREATE TABLE IF NOT EXISTS standings (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),

    -- Position
    rank INTEGER NOT NULL,
    points INTEGER NOT NULL,

    -- Form and status
    form VARCHAR(10),
    status VARCHAR(50),
    description VARCHAR(255),

    -- Matches
    played INTEGER DEFAULT 0,
    win INTEGER DEFAULT 0,
    draw INTEGER DEFAULT 0,
    lose INTEGER DEFAULT 0,

    -- Goals
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_diff INTEGER DEFAULT 0,

    -- Home record
    home_played INTEGER DEFAULT 0,
    home_win INTEGER DEFAULT 0,
    home_draw INTEGER DEFAULT 0,
    home_lose INTEGER DEFAULT 0,
    home_goals_for INTEGER DEFAULT 0,
    home_goals_against INTEGER DEFAULT 0,

    -- Away record
    away_played INTEGER DEFAULT 0,
    away_win INTEGER DEFAULT 0,
    away_draw INTEGER DEFAULT 0,
    away_lose INTEGER DEFAULT 0,
    away_goals_for INTEGER DEFAULT 0,
    away_goals_against INTEGER DEFAULT 0,

    -- Metadata
    last_update TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(league_id, season, team_id)
);

CREATE INDEX IF NOT EXISTS ix_standings_league_id ON standings(league_id);
CREATE INDEX IF NOT EXISTS ix_standings_season ON standings(season);
CREATE INDEX IF NOT EXISTS ix_standings_team_id ON standings(team_id);

-- Table: lineups (match lineups and formations)
CREATE TABLE IF NOT EXISTS lineups (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    team_id INTEGER NOT NULL REFERENCES teams(id),

    -- Formation
    formation VARCHAR(20),

    -- Coach
    coach_id INTEGER,
    coach_name VARCHAR(100),
    coach_photo VARCHAR(255),

    -- Players (JSON)
    starting_xi JSONB,
    substitutes JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(fixture_id, team_id)
);

CREATE INDEX IF NOT EXISTS ix_lineups_fixture_id ON lineups(fixture_id);
CREATE INDEX IF NOT EXISTS ix_lineups_team_id ON lineups(team_id);

-- Table: player_statistics (detailed player match stats)
CREATE TABLE IF NOT EXISTS player_statistics (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    team_id INTEGER NOT NULL REFERENCES teams(id),

    -- Player info
    player_id INTEGER NOT NULL,
    player_name VARCHAR(100),
    player_number INTEGER,
    player_position VARCHAR(20),
    player_grid VARCHAR(10),

    -- Match statistics
    minutes_played INTEGER,
    rating VARCHAR(10),
    captain BOOLEAN DEFAULT FALSE,
    substitute BOOLEAN DEFAULT FALSE,

    -- Performance stats
    offsides INTEGER,
    shots_total INTEGER,
    shots_on INTEGER,
    goals_total INTEGER,
    goals_conceded INTEGER,
    goals_assists INTEGER,

    -- Passing
    passes_total INTEGER,
    passes_key INTEGER,
    passes_accuracy INTEGER,

    -- Dribbles
    dribbles_attempts INTEGER,
    dribbles_success INTEGER,
    dribbles_past INTEGER,

    -- Duels
    duels_total INTEGER,
    duels_won INTEGER,

    -- Tackles/Blocks
    tackles_total INTEGER,
    tackles_blocks INTEGER,
    tackles_interceptions INTEGER,

    -- Cards
    yellow_cards INTEGER,
    red_cards INTEGER,

    -- Fouls
    fouls_drawn INTEGER,
    fouls_committed INTEGER,

    -- Penalty
    penalty_won INTEGER,
    penalty_committed INTEGER,
    penalty_scored INTEGER,
    penalty_missed INTEGER,
    penalty_saved INTEGER,

    -- Goalkeeper
    saves INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_player_statistics_fixture_id ON player_statistics(fixture_id);
CREATE INDEX IF NOT EXISTS ix_player_statistics_player_id ON player_statistics(player_id);

-- Table: top_scorers (league top scorers and assists)
CREATE TABLE IF NOT EXISTS top_scorers (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),

    -- Player info
    player_id INTEGER NOT NULL,
    player_name VARCHAR(100),
    player_firstname VARCHAR(50),
    player_lastname VARCHAR(50),
    player_age INTEGER,
    player_nationality VARCHAR(50),
    player_height VARCHAR(20),
    player_weight VARCHAR(20),
    player_photo VARCHAR(255),
    player_position VARCHAR(20),

    -- Statistics
    games_appearances INTEGER DEFAULT 0,
    games_minutes INTEGER DEFAULT 0,
    games_lineups INTEGER DEFAULT 0,
    games_rating VARCHAR(10),

    -- Goals
    goals_total INTEGER DEFAULT 0,
    goals_assists INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    goals_saves INTEGER DEFAULT 0,

    -- Shots
    shots_total INTEGER DEFAULT 0,
    shots_on INTEGER DEFAULT 0,

    -- Passes
    passes_total INTEGER DEFAULT 0,
    passes_key INTEGER DEFAULT 0,
    passes_accuracy INTEGER DEFAULT 0,

    -- Tackles
    tackles_total INTEGER DEFAULT 0,
    tackles_blocks INTEGER DEFAULT 0,
    tackles_interceptions INTEGER DEFAULT 0,

    -- Duels
    duels_total INTEGER DEFAULT 0,
    duels_won INTEGER DEFAULT 0,

    -- Dribbles
    dribbles_attempts INTEGER DEFAULT 0,
    dribbles_success INTEGER DEFAULT 0,

    -- Fouls
    fouls_drawn INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,

    -- Cards
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,

    -- Penalty
    penalty_scored INTEGER DEFAULT 0,
    penalty_missed INTEGER DEFAULT 0,
    penalty_saved INTEGER DEFAULT 0,

    -- Metadata
    last_update TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(league_id, season, player_id)
);

CREATE INDEX IF NOT EXISTS ix_top_scorers_league_id ON top_scorers(league_id);
CREATE INDEX IF NOT EXISTS ix_top_scorers_player_id ON top_scorers(player_id);

-- Table: api_predictions (API-Football's own predictions)
CREATE TABLE IF NOT EXISTS api_predictions (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id) UNIQUE,

    -- Winner prediction
    winner_id INTEGER,
    winner_name VARCHAR(100),
    winner_comment VARCHAR(255),
    win_or_draw BOOLEAN,

    -- Under/Over prediction
    under_over VARCHAR(20),

    -- Goals prediction
    goals_home VARCHAR(10),
    goals_away VARCHAR(10),

    -- Advice
    advice VARCHAR(255),

    -- Winning percentages
    percent_home VARCHAR(10),
    percent_draw VARCHAR(10),
    percent_away VARCHAR(10),

    -- Comparison data (JSON)
    comparison JSONB,
    h2h JSONB,
    league_stats JSONB,
    teams_stats JSONB,

    -- Metadata
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_api_predictions_fixture_id ON api_predictions(fixture_id);

-- Table: h2h_matches (head-to-head history)
CREATE TABLE IF NOT EXISTS h2h_matches (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id) UNIQUE,

    -- Teams involved (for quick lookup)
    team1_id INTEGER NOT NULL REFERENCES teams(id),
    team2_id INTEGER NOT NULL REFERENCES teams(id),

    -- League and season
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,

    -- Match details
    match_date TIMESTAMP NOT NULL,
    home_team_id INTEGER NOT NULL REFERENCES teams(id),
    away_team_id INTEGER NOT NULL REFERENCES teams(id),

    -- Score
    home_score INTEGER,
    away_score INTEGER,

    -- Status
    status VARCHAR(20),

    -- Winner
    winner_id INTEGER REFERENCES teams(id),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_h2h_teams ON h2h_matches(team1_id, team2_id);
CREATE INDEX IF NOT EXISTS ix_h2h_teams_reverse ON h2h_matches(team2_id, team1_id);
CREATE INDEX IF NOT EXISTS ix_h2h_date ON h2h_matches(match_date);
CREATE INDEX IF NOT EXISTS ix_h2h_fixture_id ON h2h_matches(fixture_id);
