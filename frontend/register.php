<?php
require_once 'config.php';
require_once 'includes/APIClient.php';

$error = '';
$success = '';

// Redirect if already logged in
if (isLoggedIn()) {
    header('Location: index.php');
    exit;
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $fullName = $_POST['full-name'] ?? '';
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    $confirmPassword = $_POST['confirm-password'] ?? '';
    $agreedToTerms = isset($_POST['terms']);

    // Validation
    if (empty($fullName) || empty($email) || empty($password)) {
        $error = 'Please fill in all required fields';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Please enter a valid email address';
    } elseif (strlen($password) < 8) {
        $error = 'Password must be at least 8 characters long';
    } elseif ($password !== $confirmPassword) {
        $error = 'Passwords do not match';
    } elseif (!$agreedToTerms) {
        $error = 'Please agree to the terms and conditions';
    } else {
        $api = new APIClient();
        $result = $api->register($email, $password, $fullName);

        if ($result['success']) {
            $success = 'Registration successful! You can now login.';
            // Auto-login after successful registration
            $loginResult = $api->login($email, $password);
            if ($loginResult['success']) {
                header('Refresh: 2; URL=index.php');
            } else {
                header('Refresh: 2; URL=login_new.php');
            }
        } else {
            $error = $result['error'] ?? 'Registration failed. Please try again.';
        }
    }
}

$pageTitle = "Register - Super Stats Football";
$pageDescription = "Create your Super Stats Football account";
include 'includes/auth-header.php';
?>

  <!-- Content -->
  <div class="container-xxl">
    <div class="authentication-wrapper authentication-basic container-p-y">
      <div class="authentication-inner">
        <!-- Register Card -->
        <div class="card px-sm-6 px-0">
          <div class="card-body">
            <?php include 'includes/auth-logo.php'; ?>
            <h4 class="mb-1 text-center">Join Super Stats Football!</h4>
            <p class="mb-6">Create your account to access premium football statistics</p>

            <?php if ($error): ?>
            <div class="alert alert-danger alert-dismissible" role="alert">
              <i class="bx bx-error me-2"></i><?php echo htmlspecialchars($error); ?>
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            <?php endif; ?>

            <?php if ($success): ?>
            <div class="alert alert-success alert-dismissible" role="alert">
              <i class="bx bx-check me-2"></i><?php echo htmlspecialchars($success); ?>
            </div>
            <?php endif; ?>

            <form id="formAuthentication" class="mb-6" method="POST" action="register_new.php">
              <div class="mb-6">
                <label for="full-name" class="form-label">Full Name</label>
                <input type="text" class="form-control" id="full-name" name="full-name"
                  placeholder="Enter your full name" autofocus required
                  value="<?php echo htmlspecialchars($_POST['full-name'] ?? ''); ?>" />
              </div>
              <div class="mb-6">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email"
                  placeholder="Enter your email" required
                  value="<?php echo htmlspecialchars($_POST['email'] ?? ''); ?>" />
              </div>
              <div class="mb-6 form-password-toggle">
                <label class="form-label" for="password">Password</label>
                <div class="input-group input-group-merge">
                  <input type="password" id="password" class="form-control" name="password"
                    placeholder="&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;"
                    aria-describedby="password" required />
                  <span class="input-group-text cursor-pointer"><i class="icon-base bx bx-hide"></i></span>
                </div>
                <small class="text-muted">Minimum 8 characters</small>
              </div>
              <div class="mb-6 form-password-toggle">
                <label class="form-label" for="confirm-password">Confirm Password</label>
                <div class="input-group input-group-merge">
                  <input type="password" id="confirm-password" class="form-control" name="confirm-password"
                    placeholder="&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;"
                    aria-describedby="confirm-password" required />
                  <span class="input-group-text cursor-pointer"><i class="icon-base bx bx-hide"></i></span>
                </div>
              </div>
              <div class="mb-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="terms" name="terms" required />
                  <label class="form-check-label" for="terms">
                    I agree to the <a href="terms-and-conditions.php" target="_blank">Terms & Conditions</a> and
                    <a href="privacy-policy.php" target="_blank">Privacy Policy</a>
                  </label>
                </div>
              </div>
              <div class="mb-6">
                <button class="btn btn-primary d-grid w-100" type="submit">Create Account</button>
              </div>
            </form>

            <p class="text-center">
              <span>Already have an account?</span>
              <a href="login_new.php">
                <span>Sign in instead</span>
              </a>
            </p>
          </div>
        </div>
        <!-- /Register Card -->
      </div>
    </div>
  </div>
  <!-- / Content -->

<?php include 'includes/auth-footer.php'; ?>
