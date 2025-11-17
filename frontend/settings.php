<?php
require_once 'config.php';
require_once 'includes/APIClient.php';

// Require authentication
requireAuth();

$pageTitle = "Settings - Super Stats Football";
$pageDescription = "Manage your account settings and preferences";
$activePage = "settings";

// Get user info
$user = $_SESSION['user'] ?? [];

include 'includes/app-header.php';
?>

<!-- Content wrapper -->
<div class="content-wrapper">
    <!-- Content -->
    <div class="container-xxl flex-grow-1 container-p-y">
        <h4 class="mb-4">Settings</h4>

        <div class="row">
            <!-- Left Column -->
            <div class="col-md-8">
                <!-- Notification Settings -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bx bx-bell me-2"></i>Notification Preferences</h5>
                    </div>
                    <div class="card-body">
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="emailNotifications" disabled>
                            <label class="form-check-label" for="emailNotifications">
                                Email Notifications
                                <small class="d-block text-muted">Receive updates about predictions and account</small>
                            </label>
                        </div>

                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="matchAlerts" disabled>
                            <label class="form-check-label" for="matchAlerts">
                                Match Alerts
                                <small class="d-block text-muted">Get notified about upcoming matches</small>
                            </label>
                        </div>

                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="weeklyReport" disabled>
                            <label class="form-check-label" for="weeklyReport">
                                Weekly Performance Report
                                <small class="d-block text-muted">Receive weekly prediction accuracy reports</small>
                            </label>
                        </div>

                        <div class="alert alert-info mt-3 mb-0">
                            <i class="bx bx-info-circle me-2"></i>
                            Notification settings coming soon!
                        </div>
                    </div>
                </div>

                <!-- Display Preferences -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bx bx-palette me-2"></i>Display Preferences</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="timezone" class="form-label">Timezone</label>
                            <select class="form-select" id="timezone" disabled>
                                <option>UTC (Coordinated Universal Time)</option>
                                <option>EST (Eastern Standard Time)</option>
                                <option>PST (Pacific Standard Time)</option>
                                <option>GMT (Greenwich Mean Time)</option>
                            </select>
                            <small class="text-muted">Match times will be displayed in your timezone</small>
                        </div>

                        <div class="mb-3">
                            <label for="dateFormat" class="form-label">Date Format</label>
                            <select class="form-select" id="dateFormat" disabled>
                                <option>MM/DD/YYYY</option>
                                <option>DD/MM/YYYY</option>
                                <option>YYYY-MM-DD</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="oddsFormat" class="form-label">Odds Format</label>
                            <select class="form-select" id="oddsFormat" disabled>
                                <option>Decimal (e.g., 2.50)</option>
                                <option>Fractional (e.g., 3/2)</option>
                                <option>American (e.g., +150)</option>
                            </select>
                        </div>

                        <div class="alert alert-info mt-3 mb-0">
                            <i class="bx bx-info-circle me-2"></i>
                            Display preferences coming soon!
                        </div>
                    </div>
                </div>

                <!-- Privacy & Security -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bx bx-shield me-2"></i>Privacy & Security</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-4">
                            <h6>Two-Factor Authentication (2FA)</h6>
                            <p class="text-muted mb-2">Add an extra layer of security to your account</p>
                            <button class="btn btn-outline-primary btn-sm" disabled>
                                <i class="bx bx-lock me-1"></i>Enable 2FA (Coming Soon)
                            </button>
                        </div>

                        <div class="mb-4">
                            <h6>Active Sessions</h6>
                            <p class="text-muted mb-2">Manage devices where you're currently logged in</p>
                            <button class="btn btn-outline-danger btn-sm" disabled>
                                <i class="bx bx-log-out me-1"></i>Sign Out All Devices (Coming Soon)
                            </button>
                        </div>

                        <div class="mb-4">
                            <h6>Download Your Data</h6>
                            <p class="text-muted mb-2">Export all your data in JSON format</p>
                            <button class="btn btn-outline-secondary btn-sm" disabled>
                                <i class="bx bx-download me-1"></i>Request Data Export (Coming Soon)
                            </button>
                        </div>

                        <div class="alert alert-info mb-0">
                            <i class="bx bx-info-circle me-2"></i>
                            Advanced security features coming soon!
                        </div>
                    </div>
                </div>

                <!-- Danger Zone -->
                <div class="card border-danger mb-4">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0"><i class="bx bx-error me-2"></i>Danger Zone</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <h6>Delete Account</h6>
                            <p class="text-muted mb-2">
                                Once you delete your account, there is no going back. Please be certain.
                            </p>
                            <button class="btn btn-danger btn-sm" disabled>
                                <i class="bx bx-trash me-1"></i>Delete My Account (Coming Soon)
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div class="col-md-4">
                <!-- Account Status -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Account Status</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <small class="text-muted">Status</small>
                            <p class="mb-0">
                                <i class="bx bx-check-circle text-success"></i> Active
                            </p>
                        </div>

                        <div class="mb-3">
                            <small class="text-muted">Current Plan</small>
                            <p class="mb-0">
                                <span class="badge badge-tier badge-<?php echo strtolower(getUserTier()); ?>">
                                    <?php echo strtoupper(getUserTier()); ?>
                                </span>
                            </p>
                        </div>

                        <div class="mb-3">
                            <small class="text-muted">Email</small>
                            <p class="mb-0"><?php echo htmlspecialchars($user['email'] ?? 'N/A'); ?></p>
                        </div>

                        <hr>

                        <div class="d-grid gap-2">
                            <a href="profile.php" class="btn btn-outline-primary btn-sm">
                                <i class="bx bx-user me-1"></i>View Profile
                            </a>
                            <a href="subscription.php" class="btn btn-outline-primary btn-sm">
                                <i class="bx bx-crown me-1"></i>Manage Subscription
                            </a>
                        </div>
                    </div>
                </div>

                <!-- API Access -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">API Access</h5>
                    </div>
                    <div class="card-body">
                        <p class="text-muted small mb-3">
                            API access is available for Pro tier and above
                        </p>

                        <?php if (in_array(getUserTier(), ['pro', 'premium', 'ultimate'])): ?>
                            <div class="mb-3">
                                <label class="form-label">API Key</label>
                                <div class="input-group">
                                    <input type="password" class="form-control" value="sk_live_xxxxxxxxxxxxx" disabled>
                                    <button class="btn btn-outline-secondary" type="button" disabled>
                                        <i class="bx bx-show"></i>
                                    </button>
                                </div>
                            </div>
                            <button class="btn btn-outline-danger btn-sm w-100" disabled>
                                <i class="bx bx-refresh me-1"></i>Regenerate Key (Coming Soon)
                            </button>
                        <?php else: ?>
                            <div class="alert alert-warning mb-0">
                                <small>
                                    <i class="bx bx-info-circle me-1"></i>
                                    Upgrade to Pro or higher to access API
                                </small>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>

                <!-- Help & Support -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Help & Support</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li class="mb-2">
                                <a href="#" class="text-decoration-none">
                                    <i class="bx bx-help-circle me-2"></i>Help Center
                                </a>
                            </li>
                            <li class="mb-2">
                                <a href="#" class="text-decoration-none">
                                    <i class="bx bx-book me-2"></i>Documentation
                                </a>
                            </li>
                            <li class="mb-2">
                                <a href="#" class="text-decoration-none">
                                    <i class="bx bx-message-square me-2"></i>Contact Support
                                </a>
                            </li>
                            <li class="mb-0">
                                <a href="#" class="text-decoration-none">
                                    <i class="bx bx-bug me-2"></i>Report a Bug
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- / Content -->
</div>
<!-- / Content wrapper -->

<?php include 'includes/app-footer.php'; ?>
