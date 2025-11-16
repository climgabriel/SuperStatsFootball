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
    $email = $_POST['email-username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (empty($email) || empty($password)) {
        $error = 'Please enter both email and password';
    } else {
        $api = new APIClient();
        $result = $api->login($email, $password);

        if ($result['success']) {
            // Login successful, redirect to dashboard
            $success = 'Login successful! Redirecting...';
            header('Refresh: 1; URL=index.php');
        } else {
            $error = $result['error'] ?? 'Invalid email or password';
        }
    }
}

$pageTitle = "Login - Super Stats Football";
$pageDescription = "Login to Super Stats Football Dashboard";
include 'includes/auth-header.php';
?>

  <!-- Content -->
  <div class="container-xxl">
    <div class="authentication-wrapper authentication-basic container-p-y">
      <div class="authentication-inner">
        <!-- Login -->
        <div class="card px-sm-6 px-0">
          <div class="card-body">
            <?php include 'includes/auth-logo.php'; ?>
            <h4 class="mb-1 text-center">Welcome to Super Stats Football!</h4>
            <p class="mb-6">Please sign-in to your account to access football statistics</p>

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

            <form id="formAuthentication" class="mb-6" method="POST" action="login.php">
              <div class="mb-6">
                <label for="email" class="form-label">Email or Username</label>
                <input type="text" class="form-control" id="email" name="email-username"
                  placeholder="Enter your email or username" autofocus required
                  value="<?php echo htmlspecialchars($_POST['email-username'] ?? ''); ?>" />
              </div>
              <div class="mb-6 form-password-toggle">
                <label class="form-label" for="password">Password</label>
                <div class="input-group input-group-merge">
                  <input type="password" id="password" class="form-control" name="password"
                    placeholder="&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;"
                    aria-describedby="password" required />
                  <span class="input-group-text cursor-pointer"><i class="icon-base bx bx-hide"></i></span>
                </div>
              </div>
              <div class="mb-8">
                <div class="d-flex justify-content-between">
                  <div class="form-check mb-0">
                    <input class="form-check-input" type="checkbox" id="remember-me" name="remember-me" />
                    <label class="form-check-label" for="remember-me"> Remember Me </label>
                  </div>
                  <a href="forgot-password.php">
                    <span>Forgot Password?</span>
                  </a>
                </div>
              </div>
              <div class="mb-6">
                <button class="btn btn-primary d-grid w-100" type="submit">Login</button>
              </div>
            </form>

            <p class="text-center">
              <span>New on our platform?</span>
              <a href="register.php">
                <span>Create an account</span>
              </a>
            </p>
          </div>
        </div>
        <!-- /Login -->
      </div>
    </div>
  </div>
  <!-- / Content -->

<?php include 'includes/auth-footer.php'; ?>
