"""
League Configuration for SuperStatsFootball
Maps all leagues to subscription tiers and defines sync priority.
"""

from typing import Dict, List

# Tier mapping for league access
LEAGUE_TIER_MAP = {
    # FREE TIER (3 leagues) - Most popular worldwide
    "free": [
        152,  # England: Premier League
        140,  # Spain: La Liga
        78,   # Germany: Bundesliga
    ],

    # STARTER TIER (10 leagues) - Major European + Top International
    "starter": [
        207,  # Italy: Serie A
        61,   # France: Ligue 1
        244,  # Netherlands: Eredivisie
        264,  # Portugal: Primeira Liga
        99,   # Brazil: Serie A
        332,  # USA: MLS
        235,  # Mexico: Liga MX
    ],

    # PRO TIER (25 leagues) - All top European + Major competitions
    "pro": [
        # European competitions
        3,    # UEFA Champions League
        4,    # UEFA Europa League
        683,  # UEFA Conference League

        # More European leagues
        124,  # Croatia: HNL
        178,  # Greece: Super League 1
        322,  # Turkey: Süper Lig
        288,  # Serbia: Super Liga
        325,  # Ukraine: Premier League
        259,  # Poland: Ekstraklasa

        # Americas
        44,   # Argentina: Liga Profesional
        115,  # Chile: Primera División
        120,  # Colombia: Primera A

        # Asia/Africa
        209,  # Japan: J1 League
        118,  # Chinese Super League
        195,  # Iran: Persian Gulf Pro League
    ],

    # PREMIUM TIER (50+ leagues) - Extensive global coverage
    "premium": [
        # England lower divisions
        153,  # Championship
        154,  # League One
        145,  # League Two

        # More European 1st divisions
        56,   # Austria: Bundesliga
        63,   # Belgium: First Division A
        135,  # Denmark: Superliga
        279,  # Scotland: Premiership
        308,  # Switzerland: Super League
        253,  # Norway: Eliteserien
        307,  # Sweden: Allsvenskan
        200,  # Ireland: Premier Division

        # European 2nd divisions
        171,  # Germany: 2. Bundesliga
        206,  # Italy: Serie B
        164,  # France: Ligue 2
        301,  # Spain: Segunda División

        # Asia expanded
        212,  # Japan: J2 League
        49,   # Australia: A-League
        566,  # India: Indian Super League
        314,  # Thailand: Thai League 1
        232,  # Malaysia: Super League

        # Americas expanded
        75,   # Brazil: Serie B
        333,  # Uruguay: Primera División
        257,  # Peru: Primera División
        255,  # Paraguay: Division Profesional

        # Africa
        141,  # Egypt: Premier League
        239,  # Morocco: Botola Pro
        177,  # Ghana: Premier League
        278,  # Saudi Arabia: Saudi League

        # International
        10,   # AFC Champions League Elite
        346,  # CAF Champions League
    ],

    # ULTIMATE TIER (100+ leagues) - ALL leagues
    "ultimate": [
        # All remaining leagues from the comprehensive list
        # World competitions
        28,   # World Cup
        1,    # UEFA European Championship
        788,  # Asia Champions Cup
        898,  # African Championship

        # Albania
        31, 32,

        # Algeria
        34, 35,

        # Armenia
        45,

        # Azerbaijan
        57,

        # Bahrain
        59,

        # Bangladesh
        60,

        # Barbados
        403,

        # Belarus
        61,

        # Bolivia
        69,

        # Bosnia
        71,

        # Botswana
        490,

        # Bulgaria
        111,

        # Cameroon
        112,

        # Canada
        659, 407,

        # Costa Rica
        121,

        # Cyprus
        130,

        # Czech Republic
        134, 133,

        # Ecuador
        140,

        # Estonia
        156,

        # Faroe Islands
        157,

        # Finland
        352, 353,

        # Georgia
        170,

        # Gibraltar
        345,

        # Guatemala
        182,

        # Hong Kong
        186,

        # Hungary
        191, 188,

        # Iceland
        192,

        # Indonesia
        194,

        # Iraq
        495,

        # Israel
        202,

        # Ivory Coast
        123,

        # Jamaica
        208,

        # Jordan
        213,

        # Kazakhstan
        214,

        # Kenya
        216,

        # Kosovo
        544,

        # Kuwait
        220,

        # Latvia
        223,

        # Lebanon
        224,

        # Libya
        225,

        # Lithuania
        227,

        # Luxembourg
        228,

        # Malta
        234, 233,

        # Mauritania
        559,

        # Mauritius
        557,

        # Moldova
        237, 238,

        # Mongolia
        446,

        # Montenegro
        398,

        # Myanmar
        589,

        # Nepal
        496,

        # New Zealand
        246,

        # Nicaragua
        247,

        # Northern Ireland
        251,

        # Oman
        254,

        # Pakistan
        693,

        # Panama
        406,

        # Philippines
        623,

        # Qatar
        269, 397,

        # Romania
        272, 271, 270,

        # Russia
        344,

        # San Marino
        276,

        # Senegal
        497,

        # Singapore
        289,

        # Slovakia
        293,

        # Slovenia
        296,

        # South Africa
        530,

        # Syria
        313,

        # Uganda
        555,

        # UAE
        328, 483,

        # Uzbekistan
        335,

        # Venezuela
        337,

        # Vietnam
        339,

        # Wales
        341,

        # Zambia
        342,

        # Additional 2nd/3rd divisions
        176,  # Germany: 3. Liga
        359,  # Italy: Serie C
        167,  # France: National 1
        319,  # Turkey: 1. Lig
        318,  # Turkey: 2. Lig
        263,  # Poland: I Liga
        245,  # Netherlands: Eerste Divisie
        282,  # Scotland: Championship
        312,  # Switzerland: Challenge League
        305,  # Sweden: Superettan
        138,  # Denmark: 1. Division
        53,   # Austria: 2. Liga
        7961, # Croatia: Second NL
        439,  # Greece: Super League 2
        116,  # Chile: Primera B
        517,  # Colombia: Primera B
        40,   # Argentina: Prim B Metro
        236,  # Mexico: Liga de Expansión MX
        256,  # Paraguay: Division Intermedia
        258,  # Peru: Segunda División
        334,  # Uruguay: Segunda División
        277,  # Saudi Arabia: Division 1
        324,  # Ukraine: Persha Liga
        701,  # Egypt: Second Division A
        602,  # Thailand: Thai League 2
        193,  # India: I-League
        252,  # Norway: NM Cupen
        574,  # Belgium: Super League
        8102, # USA: USL Super League
        353,  # Finland: Ykkönen
    ]
}


# Complete league metadata
LEAGUE_METADATA = {
    # Format: league_id: {"name": str, "country": str, "tier": str, "priority": int}

    # Free tier leagues (highest priority)
    152: {"name": "Premier League", "country": "England", "tier": "free", "priority": 100},
    140: {"name": "La Liga", "country": "Spain", "tier": "free", "priority": 95},
    78: {"name": "Bundesliga", "country": "Germany", "tier": "free", "priority": 90},

    # Starter tier
    207: {"name": "Serie A", "country": "Italy", "tier": "starter", "priority": 85},
    61: {"name": "Ligue 1", "country": "France", "tier": "starter", "priority": 80},
    244: {"name": "Eredivisie", "country": "Netherlands", "tier": "starter", "priority": 75},
    264: {"name": "Primeira Liga", "country": "Portugal", "tier": "starter", "priority": 70},
    99: {"name": "Serie A", "country": "Brazil", "tier": "starter", "priority": 65},
    332: {"name": "MLS", "country": "USA", "tier": "starter", "priority": 60},
    235: {"name": "Liga MX", "country": "Mexico", "tier": "starter", "priority": 55},

    # Pro tier
    3: {"name": "UEFA Champions League", "country": "Europe", "tier": "pro", "priority": 98},
    4: {"name": "UEFA Europa League", "country": "Europe", "tier": "pro", "priority": 93},
    683: {"name": "UEFA Conference League", "country": "Europe", "tier": "pro", "priority": 88},

    # Add more as needed... (would be too long to list all 150+)
}


# Season retention policy
SEASON_RETENTION = {
    "current_season": True,  # Always keep
    "previous_seasons": 4,   # Keep 4 previous seasons
    "total_seasons": 5,      # Total: current + 4 previous
}


# Sync configuration
SYNC_CONFIG = {
    "batch_size": 100,           # Fixtures per batch
    "rate_limit_delay": 1.0,     # Seconds between API calls
    "retry_attempts": 3,          # Retries on failure
    "timeout": 30,                # Request timeout
    "parallel_leagues": 5,        # Sync 5 leagues in parallel
}


def get_leagues_for_tier(tier: str) -> List[int]:
    """Get all league IDs accessible for a given tier."""
    accessible_leagues = []

    tier_hierarchy = ["free", "starter", "pro", "premium", "ultimate"]
    tier_index = tier_hierarchy.index(tier) if tier in tier_hierarchy else -1

    if tier_index == -1:
        return []

    # Add all leagues from current tier and below
    for i in range(tier_index + 1):
        tier_name = tier_hierarchy[i]
        accessible_leagues.extend(LEAGUE_TIER_MAP.get(tier_name, []))

    return list(set(accessible_leagues))


def get_tier_for_league(league_id: int) -> str:
    """Get minimum tier required to access a league."""
    for tier, leagues in LEAGUE_TIER_MAP.items():
        if league_id in leagues:
            return tier
    return "ultimate"  # Default to ultimate if not found


def get_all_league_ids() -> List[int]:
    """Get all league IDs from all tiers."""
    all_leagues = []
    for leagues in LEAGUE_TIER_MAP.values():
        all_leagues.extend(leagues)
    return list(set(all_leagues))


def get_sync_priority_leagues() -> List[int]:
    """Get leagues in priority order for syncing."""
    # Free tier first, then starter, pro, premium, ultimate
    priority_order = []
    for tier in ["free", "starter", "pro", "premium", "ultimate"]:
        priority_order.extend(LEAGUE_TIER_MAP.get(tier, []))
    return priority_order
