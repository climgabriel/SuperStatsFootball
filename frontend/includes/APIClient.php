<?php
/**
 * API Client for SuperStatsFootball Backend
 *
 * Handles all API requests with authentication, error handling, and token refresh
 */

require_once __DIR__ . '/../config.php';

class APIClient {
    private $baseUrl;
    private $accessToken;
    private $refreshToken;

    public function __construct() {
        $this->baseUrl = API_BASE_URL . API_PREFIX;
        $this->accessToken = getAccessToken();
        $this->refreshToken = getRefreshToken();
    }

    /**
     * Make HTTP request to API
     */
    private function makeRequest($method, $endpoint, $data = null, $requireAuth = false) {
        $url = $this->baseUrl . $endpoint;

        $headers = [
            'Content-Type: application/json',
            'Accept: application/json'
        ];

        if ($requireAuth && $this->accessToken) {
            $headers[] = 'Authorization: Bearer ' . $this->accessToken;
        }

        $options = [
            'http' => [
                'method' => $method,
                'header' => implode("\r\n", $headers),
                'timeout' => 30,
                'ignore_errors' => true
            ]
        ];

        if ($data && in_array($method, ['POST', 'PUT', 'PATCH'])) {
            $options['http']['content'] = json_encode($data);
        }

        $context = stream_context_create($options);
        $response = @file_get_contents($url, false, $context);

        if ($response === false) {
            return [
                'success' => false,
                'error' => 'Failed to connect to API',
                'data' => null
            ];
        }

        // Parse HTTP response code
        $statusCode = 200;
        if (isset($http_response_header) && count($http_response_header) > 0) {
            preg_match('/HTTP\/\d\.\d\s+(\d+)/', $http_response_header[0], $matches);
            $statusCode = isset($matches[1]) ? (int)$matches[1] : 200;
        }

        $decoded = json_decode($response, true);

        // Handle 401 Unauthorized - try to refresh token
        if ($statusCode === 401 && $requireAuth && $this->refreshToken) {
            $refreshResult = $this->refreshAccessToken();
            if ($refreshResult['success']) {
                // Retry the original request with new token
                return $this->makeRequest($method, $endpoint, $data, $requireAuth);
            }
        }

        return [
            'success' => $statusCode >= 200 && $statusCode < 300,
            'status_code' => $statusCode,
            'data' => $decoded,
            'error' => $decoded['detail'] ?? ($statusCode >= 400 ? 'API Error' : null)
        ];
    }

    /**
     * Authentication: Login
     */
    public function login($email, $password) {
        $result = $this->makeRequest('POST', '/auth/login', [
            'email' => $email,
            'password' => $password
        ]);

        if ($result['success'] && isset($result['data']['access_token'])) {
            $this->setTokens(
                $result['data']['access_token'],
                $result['data']['refresh_token'] ?? null
            );

            // Store user info in session
            $_SESSION['user'] = $result['data']['user'] ?? [];
            $_SESSION['access_token'] = $result['data']['access_token'];
            $_SESSION['refresh_token'] = $result['data']['refresh_token'] ?? null;
        }

        return $result;
    }

    /**
     * Authentication: Register
     */
    public function register($email, $password, $fullName) {
        return $this->makeRequest('POST', '/auth/register', [
            'email' => $email,
            'password' => $password,
            'full_name' => $fullName
        ]);
    }

    /**
     * Authentication: Logout
     */
    public function logout() {
        $result = $this->makeRequest('POST', '/auth/logout', null, true);

        // Clear session and cookies regardless of API response
        $this->clearTokens();
        session_destroy();

        return $result;
    }

    /**
     * Refresh access token
     */
    public function refreshAccessToken() {
        if (!$this->refreshToken) {
            return ['success' => false, 'error' => 'No refresh token available'];
        }

        $result = $this->makeRequest('POST', '/auth/refresh', [
            'refresh_token' => $this->refreshToken
        ]);

        if ($result['success'] && isset($result['data']['access_token'])) {
            $this->setTokens(
                $result['data']['access_token'],
                $result['data']['refresh_token'] ?? $this->refreshToken
            );

            $_SESSION['access_token'] = $result['data']['access_token'];
            if (isset($result['data']['refresh_token'])) {
                $_SESSION['refresh_token'] = $result['data']['refresh_token'];
            }
        }

        return $result;
    }

    /**
     * Get user profile
     */
    public function getUserProfile() {
        return $this->makeRequest('GET', '/users/me', null, true);
    }

    /**
     * Get predictions with odds (UNIFIED ENDPOINT)
     */
    public function getPredictionsWithOdds($daysAhead = 7, $leagueId = null, $limit = 100, $offset = 0) {
        $params = [
            'days_ahead' => $daysAhead,
            'limit' => $limit,
            'offset' => $offset
        ];

        if ($leagueId) {
            $params['league_id'] = $leagueId;
        }

        $queryString = http_build_query($params);
        $endpoint = '/combined/fixtures/predictions-with-odds?' . $queryString;

        return $this->makeRequest('GET', $endpoint, null, true);
    }

    /**
     * Get accessible leagues for user
     */
    public function getAccessibleLeagues() {
        return $this->makeRequest('GET', '/leagues/accessible/me', null, true);
    }

    /**
     * Get league tier info
     */
    public function getLeagueTierInfo() {
        return $this->makeRequest('GET', '/leagues/tier-info', null, false);
    }

    /**
     * Set authentication tokens
     */
    private function setTokens($accessToken, $refreshToken = null) {
        $this->accessToken = $accessToken;

        // Set cookies for token persistence
        setcookie(
            TOKEN_COOKIE_NAME,
            $accessToken,
            time() + (TOKEN_EXPIRY_MINUTES * 60),
            '/',
            '',
            true,  // HTTPS only
            true   // HTTP only (no JavaScript access)
        );

        if ($refreshToken) {
            $this->refreshToken = $refreshToken;
            setcookie(
                REFRESH_TOKEN_COOKIE_NAME,
                $refreshToken,
                time() + (REFRESH_TOKEN_EXPIRY_DAYS * 24 * 60 * 60),
                '/',
                '',
                true,
                true
            );
        }
    }

    /**
     * Clear authentication tokens
     */
    private function clearTokens() {
        $this->accessToken = null;
        $this->refreshToken = null;

        // Clear cookies
        setcookie(TOKEN_COOKIE_NAME, '', time() - 3600, '/');
        setcookie(REFRESH_TOKEN_COOKIE_NAME, '', time() - 3600, '/');

        // Clear session
        unset($_SESSION['user']);
        unset($_SESSION['access_token']);
        unset($_SESSION['refresh_token']);
    }

    /**
     * Check if user is authenticated
     */
    public function isAuthenticated() {
        return !empty($this->accessToken);
    }
}
