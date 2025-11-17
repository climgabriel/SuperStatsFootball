<!doctype html>
<html lang="en" class="light-style layout-wide customizer-hide" dir="ltr" data-theme="theme-default">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0" />
    <title><?php echo isset($pageTitle) ? htmlspecialchars($pageTitle) : APP_NAME; ?></title>
    <meta name="description" content="<?php echo isset($pageDescription) ? htmlspecialchars($pageDescription) : 'Football Statistics and Predictions'; ?>" />

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="assets/img/favicon/favicon.ico" />

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

    <!-- Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/boxicons@2.1.4/css/boxicons.min.css" />

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" />

    <!-- Custom Styles -->
    <style>
        :root {
            --primary-color: #696cff;
            --primary-hover: #5f61e6;
            --text-primary: #566a7f;
            --text-heading: #384551;
            --bg-body: #f5f5f9;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
        }

        .authentication-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1.5rem;
        }

        .authentication-inner {
            width: 100%;
            max-width: 450px;
        }

        .card {
            border: none;
            border-radius: 0.5rem;
            box-shadow: 0 0.25rem 1.125rem rgba(75, 70, 92, 0.1);
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .btn-primary:hover {
            background-color: var(--primary-hover);
            border-color: var(--primary-hover);
        }

        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(105, 108, 255, 0.25);
        }

        .text-primary {
            color: var(--primary-color) !important;
        }

        h4 {
            color: var(--text-heading);
            font-weight: 600;
        }

        .alert {
            border-radius: 0.375rem;
        }

        .app-brand-logo img {
            max-width: 50px;
            height: auto;
        }

        .app-brand-text {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-left: 0.5rem;
        }

        .input-group-text {
            background-color: transparent;
            border-left: 0;
        }

        .form-password-toggle .form-control {
            border-right: 0;
        }

        .cursor-pointer {
            cursor: pointer;
        }
    </style>
</head>

<body>
