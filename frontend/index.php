<?php
/**
 * SuperStatsFootball - Main Entry Point
 *
 * This is the MAIN ENTRY POINT of the application.
 * All users start here.
 *
 * Authentication Flow:
 * - If user is logged in → Redirect to dashboard (1x2_new.php)
 * - If user is NOT logged in → Redirect to login page (login_new.php)
 *
 * NO ONE can access the application without authentication.
 */

require_once 'config.php';

// Check if user is logged in
if (isLoggedIn()) {
    // User is authenticated - redirect to dashboard
    header('Location: 1x2_new.php');
    exit;
} else {
    // User is NOT authenticated - redirect to login
    header('Location: login_new.php');
    exit;
}
