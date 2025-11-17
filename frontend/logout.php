<?php
/**
 * SuperStatsFootball - Logout
 *
 * Destroys user session and redirects to login page.
 * This ensures complete logout and prevents any cached access.
 */

require_once 'config.php';

// Call API logout endpoint if logged in
if (isLoggedIn()) {
    try {
        $api = new APIClient();
        $api->logout();
    } catch (Exception $e) {
        // Log error but continue with session destruction
        error_log('Logout API call failed: ' . $e->getMessage());
    }
}

// Destroy session
session_destroy();

// Clear session array
$_SESSION = array();

// Delete cookies
if (isset($_COOKIE[SESSION_NAME])) {
    setcookie(SESSION_NAME, '', time() - 3600, '/');
}

if (isset($_COOKIE[TOKEN_COOKIE_NAME])) {
    setcookie(TOKEN_COOKIE_NAME, '', time() - 3600, '/');
}

if (isset($_COOKIE[REFRESH_TOKEN_COOKIE_NAME])) {
    setcookie(REFRESH_TOKEN_COOKIE_NAME, '', time() - 3600, '/');
}

// Redirect to login page
header('Location: login_new.php?logged_out=1');
exit;
