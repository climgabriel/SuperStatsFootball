<!doctype html>
<html lang="en" class="light-style layout-navbar-fixed layout-menu-fixed" dir="ltr" data-theme="theme-default">
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

    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" />

    <!-- Custom Styles -->
    <style>
        :root {
            --primary-color: #696cff;
            --primary-hover: #5f61e6;
            --success-color: #71dd37;
            --danger-color: #ff3e1d;
            --warning-color: #ffab00;
            --info-color: #03c3ec;
            --text-primary: #566a7f;
            --text-heading: #384551;
            --bg-body: #f5f5f9;
            --sidebar-bg: #fff;
            --navbar-bg: #fff;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            padding-top: 70px;
        }

        .navbar {
            background-color: var(--navbar-bg);
            box-shadow: 0 0.125rem 0.25rem rgba(75, 70, 92, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }

        .navbar-brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color) !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .navbar-brand svg {
            width: 40px;
            height: 40px;
        }

        .nav-link {
            color: var(--text-primary);
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: color 0.2s;
        }

        .nav-link:hover, .nav-link.active {
            color: var(--primary-color);
        }

        .badge-tier {
            font-size: 0.75rem;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-free { background-color: #e7e7ff; color: #696cff; }
        .badge-starter { background-color: #d4f4dd; color: #28a745; }
        .badge-pro { background-color: #fff3cd; color: #ff9800; }
        .badge-premium { background-color: #ffebee; color: #f44336; }
        .badge-ultimate { background-color: #e1f5fe; color: #03a9f4; }

        .dropdown-menu {
            border: none;
            box-shadow: 0 0.25rem 1rem rgba(75, 70, 92, 0.15);
            border-radius: 0.5rem;
        }

        .dropdown-item {
            padding: 0.75rem 1.25rem;
            transition: background-color 0.2s;
        }

        .dropdown-item:hover {
            background-color: #f5f5f9;
        }

        .dropdown-divider {
            margin: 0.5rem 0;
        }

        .card {
            border: none;
            border-radius: 0.5rem;
            box-shadow: 0 0.125rem 0.5rem rgba(75, 70, 92, 0.1);
            margin-bottom: 1.5rem;
        }

        .card-header {
            background-color: transparent;
            border-bottom: 1px solid #e7e7e7;
            padding: 1.25rem 1.5rem;
        }

        .card-body {
            padding: 1.5rem;
        }

        h4 {
            color: var(--text-heading);
            font-weight: 600;
        }

        .table {
            color: var(--text-primary);
        }

        .table thead th {
            color: var(--text-heading);
            font-weight: 600;
            border-bottom: 2px solid #e7e7e7;
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .btn-primary:hover {
            background-color: var(--primary-hover);
            border-color: var(--primary-hover);
        }

        .container-xxl {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }

        .loading {
            text-align: center;
            padding: 3rem;
        }

        .spinner-border {
            color: var(--primary-color);
        }
    </style>
</head>

<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg">
        <div class="container-xxl">
            <!-- Brand -->
            <a class="navbar-brand" href="index.php">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#696cff" stroke-width="2" fill="none"/>
                    <path d="M12 2L14 8H20L15 12L17 18L12 14L7 18L9 12L4 8H10L12 2Z" fill="#696cff"/>
                </svg>
                <?php echo APP_NAME; ?>
            </a>

            <!-- Navbar toggler for mobile -->
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
                <span class="navbar-toggler-icon"></span>
            </button>

            <!-- Navbar content -->
            <div class="collapse navbar-collapse" id="navbarContent">
                <ul class="navbar-nav ms-auto align-items-center">
                    <!-- Navigation Links -->
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($activePage) && $activePage === '1x2') ? 'active' : ''; ?>" href="1x2_new.php">
                            <i class='bx bx-bar-chart-alt-2 me-1'></i> Predictions
                        </a>
                    </li>

                    <!-- User Tier Badge -->
                    <li class="nav-item">
                        <span class="badge badge-tier badge-<?php echo strtolower(getUserTier()); ?>">
                            <?php echo htmlspecialchars(getUserTier()); ?>
                        </span>
                    </li>

                    <!-- User Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class='bx bx-user-circle' style="font-size: 1.5rem;"></i>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <span class="dropdown-item-text">
                                    <strong><?php echo htmlspecialchars($_SESSION['user']['full_name'] ?? $_SESSION['user']['email'] ?? 'User'); ?></strong><br>
                                    <small class="text-muted"><?php echo htmlspecialchars($_SESSION['user']['email'] ?? ''); ?></small>
                                </span>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="profile.php"><i class='bx bx-user me-2'></i> My Profile</a></li>
                            <li><a class="dropdown-item" href="subscription.php"><i class='bx bx-crown me-2'></i> Subscription</a></li>
                            <li><a class="dropdown-item" href="settings.php"><i class='bx bx-cog me-2'></i> Settings</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="logout.php"><i class='bx bx-log-out me-2'></i> Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content Area -->
