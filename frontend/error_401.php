<?php
http_response_code(401);
$pageTitle = "401 - Unauthorized";
$pageDescription = "You need to login to access this page";
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><?php echo $pageTitle; ?></title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/boxicons@2.1.4/css/boxicons.min.css" />
    <style>
        body {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', sans-serif;
        }
        .error-container {
            text-align: center;
            color: white;
        }
        .error-code {
            font-size: 120px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .error-message {
            font-size: 24px;
            margin-bottom: 30px;
        }
        .btn-login {
            background: white;
            color: #f5576c;
            padding: 12px 30px;
            border-radius: 50px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: #f5576c;
        }
        .illustration {
            font-size: 150px;
            margin-bottom: 20px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="illustration">
            <i class='bx bx-lock-alt'></i>
        </div>
        <div class="error-code">401</div>
        <div class="error-message">Unauthorized Access</div>
        <p class="mb-4" style="opacity: 0.9;">
            You need to be logged in to access this page.
        </p>
        <a href="login_new.php" class="btn-login">
            <i class='bx bx-log-in'></i>
            Login Now
        </a>
    </div>
</body>
</html>
