<?php
require_once 'config.php';
require_once 'includes/APIClient.php';

// Require authentication
requireAuth();

$pageTitle = "My Profile - Super Stats Football";
$pageDescription = "Manage your profile and account settings";
$activePage = "profile";

// Get user info
$user = $_SESSION['user'] ?? [];
$api = new APIClient();

// Handle profile update
$success = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Future: Handle profile update
    $success = 'Profile update functionality coming soon!';
}

include 'includes/app-header.php';
?>

<!-- Content wrapper -->
<div class="content-wrapper">
    <!-- Content -->
    <div class="container-xxl flex-grow-1 container-p-y">
        <h4 class="mb-4">My Profile</h4>

        <?php if ($success): ?>
        <div class="alert alert-success alert-dismissible" role="alert">
            <i class="bx bx-check me-2"></i><?php echo htmlspecialchars($success); ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        <?php endif; ?>

        <?php if ($error): ?>
        <div class="alert alert-danger alert-dismissible" role="alert">
            <i class="bx bx-error me-2"></i><?php echo htmlspecialchars($error); ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        <?php endif; ?>

        <div class="row">
            <!-- Profile Information -->
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Profile Information</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            <div class="mb-3">
                                <label for="full_name" class="form-label">Full Name</label>
                                <input type="text" class="form-control" id="full_name" name="full_name"
                                       value="<?php echo htmlspecialchars($user['full_name'] ?? ''); ?>"
                                       placeholder="Enter your full name" disabled>
                            </div>

                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="email"
                                       value="<?php echo htmlspecialchars($user['email'] ?? ''); ?>"
                                       placeholder="your@email.com" disabled>
                            </div>

                            <div class="mb-3">
                                <label for="created_at" class="form-label">Member Since</label>
                                <input type="text" class="form-control" id="created_at"
                                       value="<?php echo isset($user['created_at']) ? date('F j, Y', strtotime($user['created_at'])) : 'N/A'; ?>"
                                       disabled>
                            </div>

                            <div class="alert alert-info">
                                <i class="bx bx-info-circle me-2"></i>
                                Profile editing will be available in the next update. Contact support to make changes.
                            </div>

                            <!-- <button type="submit" class="btn btn-primary">Update Profile</button> -->
                        </form>
                    </div>
                </div>

                <!-- Change Password -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h5 class="mb-0">Change Password</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="bx bx-info-circle me-2"></i>
                            Password change functionality coming soon!
                        </div>
                    </div>
                </div>
            </div>

            <!-- Account Summary -->
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Account Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <small class="text-muted">User ID</small>
                            <p class="mb-0"><strong><?php echo htmlspecialchars($user['id'] ?? 'N/A'); ?></strong></p>
                        </div>

                        <div class="mb-3">
                            <small class="text-muted">Current Tier</small>
                            <p class="mb-0">
                                <span class="badge badge-tier badge-<?php echo strtolower(getUserTier()); ?>">
                                    <?php echo strtoupper(getUserTier()); ?>
                                </span>
                            </p>
                        </div>

                        <div class="mb-3">
                            <small class="text-muted">Email Status</small>
                            <p class="mb-0">
                                <?php if (isset($user['is_verified']) && $user['is_verified']): ?>
                                    <i class="bx bx-check-circle text-success"></i> Verified
                                <?php else: ?>
                                    <i class="bx bx-x-circle text-warning"></i> Not Verified
                                <?php endif; ?>
                            </p>
                        </div>

                        <div class="mb-3">
                            <small class="text-muted">Account Status</small>
                            <p class="mb-0">
                                <?php if (isset($user['is_active']) && $user['is_active']): ?>
                                    <i class="bx bx-check-circle text-success"></i> Active
                                <?php else: ?>
                                    <i class="bx bx-x-circle text-danger"></i> Inactive
                                <?php endif; ?>
                            </p>
                        </div>

                        <hr>

                        <div class="d-grid gap-2">
                            <a href="subscription.php" class="btn btn-primary">
                                <i class="bx bx-crown me-2"></i>Upgrade Subscription
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h5 class="mb-0">Quick Stats</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info mb-0">
                            <i class="bx bx-info-circle me-2"></i>
                            Usage statistics coming soon!
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- / Content -->
</div>
<!-- / Content wrapper -->

<?php include 'includes/app-footer.php'; ?>
