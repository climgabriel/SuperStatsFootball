<?php
http_response_code(404);
$pageTitle = "404 - Page Not Found";
$pageDescription = "The page you're looking for doesn't exist";
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .btn-home {
            background: white;
            color: #667eea;
            padding: 12px 30px;
            border-radius: 50px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-home:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: #667eea;
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
            <i class='bx bx-confused'></i>
        </div>
        <div class="error-code">404</div>
        <div class="error-message">Oops! Page not found</div>
        <p class="mb-4" style="opacity: 0.9;">
            The page you're looking for doesn't exist or has been moved.
        </p>
        <a href="index.php" class="btn-home">
            <i class='bx bx-home-alt'></i>
            Back to Home
        </a>
    </div>
</body>
</html>
