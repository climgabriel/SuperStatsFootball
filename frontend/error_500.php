<?php
http_response_code(500);
$pageTitle = "500 - Internal Server Error";
$pageDescription = "Something went wrong on our end";
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
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', sans-serif;
        }
        .error-container {
            text-align: center;
            color: #333;
        }
        .error-code {
            font-size: 120px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.1);
            color: #666;
        }
        .error-message {
            font-size: 24px;
            margin-bottom: 30px;
            color: #666;
        }
        .btn-home {
            background: #667eea;
            color: white;
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
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            color: white;
        }
        .illustration {
            font-size: 150px;
            margin-bottom: 20px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="illustration">
            <i class='bx bx-error-circle'></i>
        </div>
        <div class="error-code">500</div>
        <div class="error-message">Internal Server Error</div>
        <p class="mb-4" style="color: #666;">
            Something went wrong on our end.<br>
            We're working to fix it. Please try again later.
        </p>
        <a href="index.php" class="btn-home">
            <i class='bx bx-home-alt'></i>
            Back to Home
        </a>
    </div>
</body>
</html>
