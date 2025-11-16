<?php
/**
 * SuperStatsFootball Frontend Configuration
 *
 * Central configuration file for API endpoints and application settings
 */

// Prevent direct access
if (!defined('SSF_CONFIG')) {
    define('SSF_CONFIG', true);
}

// API Configuration
define('API_BASE_URL', 'https://superstatsfootball-production.up.railway.app');
define('API_VERSION', 'v1');
define('API_PREFIX', '/api/' . API_VERSION);

// API Endpoints
define('API_AUTH_LOGIN', API_BASE_URL . API_PREFIX . '/auth/login');
define('API_AUTH_REGISTER', API_BASE_URL . API_PREFIX . '/auth/register');
define('API_AUTH_REFRESH', API_BASE_URL . API_PREFIX . '/auth/refresh');
define('API_AUTH_LOGOUT', API_BASE_URL . API_PREFIX . '/auth/logout');

define('API_PREDICTIONS_ODDS', API_BASE_URL . API_PREFIX . '/combined/fixtures/predictions-with-odds');
define('API_FIXTURES', API_BASE_URL . API_PREFIX . '/fixtures');
define('API_LEAGUES', API_BASE_URL . API_PREFIX . '/leagues');
define('API_USER_PROFILE', API_BASE_URL . API_PREFIX . '/users/me');

// Session Configuration
define('SESSION_NAME', 'ssf_session');
define('TOKEN_COOKIE_NAME', 'ssf_access_token');
define('REFRESH_TOKEN_COOKIE_NAME', 'ssf_refresh_token');
define('TOKEN_EXPIRY_MINUTES', 30);
define('REFRESH_TOKEN_EXPIRY_DAYS', 7);

// Application Settings
define('APP_NAME', 'Super Stats Football');
define('APP_VERSION', '1.0.0');
define('ENVIRONMENT', 'production'); // 'development' or 'production'

// Error Reporting (disable in production)
if (ENVIRONMENT === 'development') {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
} else {
    error_reporting(0);
    ini_set('display_errors', 0);
}

// Timezone
date_default_timezone_set('UTC');

// Helper Functions
function isLoggedIn() {
    return isset($_SESSION['user']) && isset($_SESSION['access_token']);
}

function getUserTier() {
    return $_SESSION['user']['tier'] ?? 'free';
}

function getAccessToken() {
    return $_SESSION['access_token'] ?? $_COOKIE[TOKEN_COOKIE_NAME] ?? null;
}

function getRefreshToken() {
    return $_SESSION['refresh_token'] ?? $_COOKIE[REFRESH_TOKEN_COOKIE_NAME] ?? null;
}

function redirectToLogin() {
    header('Location: login.php');
    exit;
}

function requireAuth() {
    if (!isLoggedIn()) {
        redirectToLogin();
    }
}

// Start session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_name(SESSION_NAME);
    session_start();
}
