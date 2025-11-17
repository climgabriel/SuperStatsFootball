<?php
require_once 'config.php';
require_once 'includes/APIClient.php';

// Require authentication
requireAuth();

$pageTitle = "Subscription - Super Stats Football";
$pageDescription = "Manage your subscription and upgrade your plan";
$activePage = "subscription";

// Get user info
$user = $_SESSION['user'] ?? [];
$currentTier = getUserTier();

include 'includes/app-header.php';
?>

<!-- Content wrapper -->
<div class="content-wrapper">
    <!-- Content -->
    <div class="container-xxl flex-grow-1 container-p-y">
        <h4 class="mb-4">Subscription Plans</h4>

        <!-- Current Plan -->
        <div class="alert alert-primary d-flex align-items-center mb-4" role="alert">
            <i class="bx bx-info-circle me-3" style="font-size: 1.5rem;"></i>
            <div>
                <strong>Your Current Plan:</strong>
                <span class="badge badge-tier badge-<?php echo strtolower($currentTier); ?> ms-2">
                    <?php echo strtoupper($currentTier); ?>
                </span>
            </div>
        </div>

        <!-- Pricing Cards -->
        <div class="row g-4">
            <!-- Free Tier -->
            <div class="col-lg-3 col-md-6">
                <div class="card <?php echo $currentTier === 'free' ? 'border-primary' : ''; ?>">
                    <div class="card-header text-center">
                        <h5 class="mb-0">Free</h5>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <h2 class="mb-0">$0</h2>
                            <small class="text-muted">per month</small>
                        </div>

                        <ul class="list-unstyled mb-4">
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>4 ML Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>Basic Statistics</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>3 Statistical Models</li>
                            <li class="mb-2"><i class="bx bx-x text-muted me-2"></i>Advanced Predictions</li>
                            <li class="mb-2"><i class="bx bx-x text-muted me-2"></i>Premium Leagues</li>
                        </ul>

                        <?php if ($currentTier === 'free'): ?>
                            <button class="btn btn-secondary w-100" disabled>Current Plan</button>
                        <?php else: ?>
                            <button class="btn btn-outline-primary w-100" disabled>Downgrade</button>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Starter Tier -->
            <div class="col-lg-3 col-md-6">
                <div class="card <?php echo $currentTier === 'starter' ? 'border-primary' : ''; ?>">
                    <div class="card-header text-center">
                        <h5 class="mb-0">Starter</h5>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <h2 class="mb-0">$9.99</h2>
                            <small class="text-muted">per month</small>
                        </div>

                        <ul class="list-unstyled mb-4">
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>9 ML Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>Advanced Statistics</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>3 Statistical Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>10+ Leagues</li>
                            <li class="mb-2"><i class="bx bx-x text-muted me-2"></i>Premium Support</li>
                        </ul>

                        <?php if ($currentTier === 'starter'): ?>
                            <button class="btn btn-primary w-100" disabled>Current Plan</button>
                        <?php else: ?>
                            <button class="btn btn-primary w-100" disabled>Upgrade Soon</button>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Pro Tier -->
            <div class="col-lg-3 col-md-6">
                <div class="card <?php echo $currentTier === 'pro' ? 'border-primary' : ''; ?> border-warning">
                    <div class="card-header text-center bg-warning text-white">
                        <h5 class="mb-0">Pro <i class="bx bx-star"></i></h5>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <h2 class="mb-0">$19.99</h2>
                            <small class="text-muted">per month</small>
                        </div>

                        <ul class="list-unstyled mb-4">
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>15 ML Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>Premium Statistics</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>3 Statistical Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>All Major Leagues</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>Priority Support</li>
                        </ul>

                        <?php if ($currentTier === 'pro'): ?>
                            <button class="btn btn-warning w-100" disabled>Current Plan</button>
                        <?php else: ?>
                            <button class="btn btn-warning w-100" disabled>Upgrade Soon</button>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Premium Tier -->
            <div class="col-lg-3 col-md-6">
                <div class="card <?php echo $currentTier === 'premium' ? 'border-primary' : ''; ?>">
                    <div class="card-header text-center">
                        <h5 class="mb-0">Premium</h5>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <h2 class="mb-0">$29.99</h2>
                            <small class="text-muted">per month</small>
                        </div>

                        <ul class="list-unstyled mb-4">
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>20 ML Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>Elite Statistics</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>3 Statistical Models</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>All Leagues Worldwide</li>
                            <li class="mb-2"><i class="bx bx-check text-success me-2"></i>24/7 Premium Support</li>
                        </ul>

                        <?php if ($currentTier === 'premium'): ?>
                            <button class="btn btn-primary w-100" disabled>Current Plan</button>
                        <?php else: ?>
                            <button class="btn btn-primary w-100" disabled>Upgrade Soon</button>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Ultimate Tier (hidden, shown on next row) -->
            <div class="col-12">
                <div class="card border-primary <?php echo $currentTier === 'ultimate' ? 'bg-light' : ''; ?>">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h4 class="mb-2">
                                    <i class="bx bx-crown text-warning me-2"></i>
                                    Ultimate Plan
                                </h4>
                                <p class="mb-3">Get access to ALL 22 ML models + 3 statistical models with advanced ensemble predictions!</p>
                                <ul class="list-inline mb-0">
                                    <li class="list-inline-item me-4"><i class="bx bx-check text-success me-2"></i>ALL 22 ML Models</li>
                                    <li class="list-inline-item me-4"><i class="bx bx-check text-success me-2"></i>Advanced Ensemble</li>
                                    <li class="list-inline-item me-4"><i class="bx bx-check text-success me-2"></i>API Access</li>
                                    <li class="list-inline-item"><i class="bx bx-check text-success me-2"></i>White-Label Option</li>
                                </ul>
                            </div>
                            <div class="col-md-4 text-center">
                                <h2 class="mb-0">$49.99<small class="text-muted">/month</small></h2>
                                <?php if ($currentTier === 'ultimate'): ?>
                                    <button class="btn btn-primary mt-3" disabled>Current Plan</button>
                                <?php else: ?>
                                    <button class="btn btn-primary mt-3" disabled>Upgrade Soon</button>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Payment Integration Notice -->
        <div class="alert alert-info mt-5">
            <h5><i class="bx bx-info-circle me-2"></i>Payment Integration Coming Soon</h5>
            <p class="mb-0">Stripe payment integration is under development. You'll be able to upgrade your plan directly from this page soon!</p>
            <p class="mb-0 mt-2"><strong>For now, contact support to upgrade your subscription.</strong></p>
        </div>

        <!-- ML Models Comparison -->
        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0">ML Models by Tier</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Tier</th>
                                <th>ML Models Included</th>
                                <th>Total Models</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="badge badge-free">FREE</span></td>
                                <td>Logistic Regression, Decision Tree, Naive Bayes, Ridge</td>
                                <td>4 ML + 3 Statistical = <strong>7 models</strong></td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-starter">STARTER</span></td>
                                <td>+ KNN, Passive Aggressive, QDA, LDA, SGD</td>
                                <td>9 ML + 3 Statistical = <strong>12 models</strong></td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-pro">PRO</span></td>
                                <td>+ Random Forest, Extra Trees, AdaBoost, Gradient Boosting, Neural Network, Bagging</td>
                                <td>15 ML + 3 Statistical = <strong>18 models</strong></td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-premium">PREMIUM</span></td>
                                <td>+ XGBoost, LightGBM, CatBoost, SVM, Stacking Ensemble</td>
                                <td>20 ML + 3 Statistical = <strong>23 models</strong></td>
                            </tr>
                            <tr class="table-primary">
                                <td><span class="badge badge-ultimate">ULTIMATE</span></td>
                                <td>+ Gaussian Process, Voting Ensemble (ALL MODELS!)</td>
                                <td>22 ML + 3 Statistical = <strong>25 models</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <!-- / Content -->
</div>
<!-- / Content wrapper -->

<?php include 'includes/app-footer.php'; ?>
