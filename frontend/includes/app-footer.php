
    <!-- Footer -->
    <footer class="content-footer footer bg-footer-theme mt-5">
        <div class="container-xxl">
            <div class="footer-container d-flex align-items-center justify-content-between py-3 flex-md-row flex-column">
                <div class="text-muted">
                    © <?php echo date('Y'); ?> <?php echo APP_NAME; ?>. All rights reserved.
                </div>
                <div>
                    <a href="terms.php" class="footer-link me-3 text-muted">Terms</a>
                    <a href="privacy.php" class="footer-link me-3 text-muted">Privacy</a>
                    <a href="support.php" class="footer-link text-muted">Support</a>
                </div>
            </div>
        </div>
    </footer>
    <!-- / Footer -->

    <!-- jQuery (required for DataTables) -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>

    <!-- Custom Application JS -->
    <script>
        // Global configuration
        const APP_CONFIG = {
            apiBaseUrl: '<?php echo API_BASE_URL; ?>',
            apiPrefix: '<?php echo API_PREFIX; ?>',
            userTier: '<?php echo getUserTier(); ?>'
        };

        // Session management - auto logout on token expiry
        let sessionTimeout;

        function resetSessionTimeout() {
            clearTimeout(sessionTimeout);
            // Auto logout after 30 minutes of inactivity
            sessionTimeout = setTimeout(() => {
                alert('Your session has expired. Please login again.');
                window.location.href = 'logout.php';
            }, <?php echo TOKEN_EXPIRY_MINUTES * 60 * 1000; ?>);
        }

        // Reset timeout on user activity
        document.addEventListener('DOMContentLoaded', function() {
            resetSessionTimeout();

            // Track user activity
            ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
                document.addEventListener(event, resetSessionTimeout);
            });
        });

        // Utility function for API calls
        async function apiCall(endpoint, options = {}) {
            const token = '<?php echo getAccessToken(); ?>';

            const headers = {
                'Content-Type': 'application/json',
                ...options.headers
            };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            try {
                const response = await fetch(APP_CONFIG.apiBaseUrl + endpoint, {
                    ...options,
                    headers
                });

                // Handle unauthorized - redirect to login
                if (response.status === 401) {
                    window.location.href = 'logout.php';
                    return null;
                }

                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        }

        // Show loading spinner
        function showLoading(element) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }
            if (element) {
                element.innerHTML = '<div class="loading"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            }
        }

        // Initialize DataTables on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize all tables with class 'datatable'
            if ($.fn.DataTable) {
                $('.datatable').DataTable({
                    pageLength: 25,
                    order: [[0, 'asc']],
                    language: {
                        search: "_INPUT_",
                        searchPlaceholder: "Search..."
                    }
                });
            }
        });
    </script>
</body>
</html>
