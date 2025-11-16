<?php
require_once 'config.php';
require_once 'includes/APIClient.php';

// Require authentication
requireAuth();

$pageTitle = "1X2 Statistics - Super Stats Football";
$pageDescription = "1X2 Match Predictions and Statistics with ML Models";
$activePage = "1x2";

// Initialize API client
$api = new APIClient();
$matches = [];
$error = null;
$userTier = getUserTier();

// Get filter parameters
$daysAhead = isset($_GET['days']) ? (int)$_GET['days'] : 7;
$leagueId = isset($_GET['league_id']) ? (int)$_GET['league_id'] : null;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 100;

try {
    // Fetch predictions with odds from unified endpoint
    $result = $api->getPredictionsWithOdds($daysAhead, $leagueId, $limit);

    if ($result['success']) {
        $responseData = $result['data'];
        $matches = $responseData['fixtures'] ?? [];
    } else {
        $error = $result['error'] ?? 'Failed to load predictions';
        error_log('API Error: ' . $error);
    }

} catch (Exception $e) {
    $error = 'System error: ' . $e->getMessage();
    error_log('Exception in 1x2.php: ' . $e->getMessage());
}

include 'includes/app-header.php';
?>

        <!-- Content wrapper -->
        <div class="content-wrapper">
          <!-- Content -->
          <div class="container-xxl flex-grow-1 container-p-y">
            <div class="d-flex justify-content-between align-items-center py-3 mb-4">
              <div>
                <h4 class="mb-0">1X2 Statistics</h4>
                <small class="text-muted">
                  Your tier: <strong><?php echo strtoupper($userTier); ?></strong> |
                  Showing: <strong><?php echo count($matches); ?> matches</strong>
                </small>
              </div>
              <button type="button" class="btn btn-primary me-3" data-bs-toggle="modal" data-bs-target="#filterModal" style="background-color: #106147; border-color: #106147;">
                <i class="bx bx-filter me-1"></i> Filter
              </button>
            </div>

            <?php if ($error): ?>
            <div class="alert alert-warning alert-dismissible" role="alert">
              <i class="bx bx-error me-2"></i><?php echo htmlspecialchars($error); ?>
              <p class="mb-0 mt-2"><small>Showing cached data or placeholder values.</small></p>
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            <?php endif; ?>

            <!-- Filter Modal -->
            <div class="modal fade" id="filterModal" tabindex="-1" aria-labelledby="filterModalLabel" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                  <div class="modal-header" style="background-color: #106147; color: white;">
                    <h5 class="modal-title" id="filterModalLabel">
                      <i class="bx bx-filter me-2"></i>Filter Options
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body">
                    <form method="GET" action="1x2.php" id="filterForm">
                      <!-- Days Ahead Filter -->
                      <div class="mb-4">
                        <label class="form-label fw-bold d-flex align-items-center">
                          <i class="bx bx-calendar me-2" style="color: #106147;"></i>Days Ahead
                        </label>
                        <select class="form-select" name="days">
                          <option value="7" <?php echo $daysAhead == 7 ? 'selected' : ''; ?>>Next 7 days</option>
                          <option value="14" <?php echo $daysAhead == 14 ? 'selected' : ''; ?>>Next 14 days</option>
                          <option value="30" <?php echo $daysAhead == 30 ? 'selected' : ''; ?>>Next 30 days</option>
                        </select>
                      </div>

                      <hr>

                      <!-- League Filter (populated dynamically) -->
                      <div class="mb-4">
                        <label class="form-label fw-bold d-flex align-items-center">
                          <i class="bx bx-trophy me-2" style="color: #106147;"></i>League
                        </label>
                        <select class="form-select" name="league_id">
                          <option value="">All Leagues</option>
                          <!-- TODO: Populate from API /leagues/accessible/me -->
                        </select>
                      </div>

                      <hr>

                      <!-- Results Limit -->
                      <div class="mb-3">
                        <label class="form-label fw-bold">Results per page</label>
                        <select class="form-select" name="limit">
                          <option value="50" <?php echo $limit == 50 ? 'selected' : ''; ?>>50</option>
                          <option value="100" <?php echo $limit == 100 ? 'selected' : ''; ?>>100</option>
                          <option value="200" <?php echo $limit == 200 ? 'selected' : ''; ?>>200</option>
                        </select>
                      </div>
                    </form>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="location.href='1x2.php'">
                      <i class="bx bx-x me-1"></i>Clear Filters
                    </button>
                    <button type="submit" form="filterForm" class="btn btn-primary" style="background-color: #106147; border-color: #106147;">
                      <i class="bx bx-check me-1"></i>Apply Filters
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Single Comprehensive Table -->
            <div class="card">
              <div class="card-body">
                <style>
                  /* [KEEPING ALL EXISTING STYLES FROM ORIGINAL FILE] */
                  .stats-table {
                    border-collapse: collapse !important;
                  }

                  .stats-table th, .stats-table td {
                    white-space: nowrap;
                    text-align: center;
                    vertical-align: middle;
                    padding: 0.5rem;
                    border: 1px solid #555555 !important;
                  }

                  .stats-table thead tr:nth-child(3) {
                    position: sticky;
                    top: 0;
                    z-index: 10;
                  }

                  .stats-table th:nth-child(3),
                  .stats-table td:nth-child(3) {
                    position: sticky;
                    left: 0;
                    z-index: 5;
                    background-color: inherit;
                    border-right: 1px solid #555555 !important;
                  }

                  .stats-table th:nth-child(4),
                  .stats-table td:nth-child(4) {
                    position: sticky;
                    left: 120px;
                    z-index: 5;
                    background-color: inherit;
                  }

                  .stats-table thead th:nth-child(3),
                  .stats-table thead th:nth-child(4) {
                    z-index: 15;
                  }

                  /* Header row colors */
                  .stats-table thead tr {
                    color: #FFFFFF !important;
                  }

                  /* Alternating row colors */
                  .stats-table tbody tr:nth-child(odd) {
                    background-color: #E8F5E9;
                  }
                  .stats-table tbody tr:nth-child(even) {
                    background-color: #F1F8F4;
                  }
                  .stats-table tbody tr:hover {
                    background-color: #C8E6D0;
                    transition: background-color 0.2s ease;
                  }

                  /* Highlight ML predictions */
                  .ml-prediction {
                    font-weight: 600;
                    color: #106147;
                  }
                </style>
                <div class="table-responsive">
                  <table class="table table-bordered table-hover stats-table" style="font-size: 0.85rem;">
                    <thead>
                      <tr style="background-color: #005440; color: white; font-weight: 600;">
                        <th rowspan="3" class="align-middle league-col">LEAGUE</th>
                        <th rowspan="3" class="align-middle date-col">DATE</th>
                        <th rowspan="3" class="align-middle team-col">1</th>
                        <th rowspan="3" class="align-middle team-col">2</th>
                        <th colspan="9" class="text-center">HALF TIME</th>
                        <th colspan="9" class="text-center">FULL TIME</th>
                        <th colspan="4" class="text-center">DRAW NO BET</th>
                        <th colspan="6" class="text-center">DOUBLE CHANCE</th>
                      </tr>
                      <tr style="background-color: #106147; color: white; font-weight: 600;">
                        <th colspan="3" class="text-center">BOOKMAKER ODDS</th>
                        <th colspan="3" class="text-center">PROBABILITY %</th>
                        <th colspan="3" class="text-center">TRUE ODDS</th>
                        <th colspan="3" class="text-center">BOOKMAKER ODDS</th>
                        <th colspan="3" class="text-center">PROBABILITY %</th>
                        <th colspan="3" class="text-center">TRUE ODDS</th>
                        <th colspan="2" class="text-center">Half Time</th>
                        <th colspan="2" class="text-center">Full Time</th>
                        <th colspan="3" class="text-center">Half Time</th>
                        <th colspan="3" class="text-center">Full Time</th>
                      </tr>
                      <tr style="background-color: #1a8a6b; color: white; font-weight: 500;">
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1</th>
                        <th class="data-col">X</th>
                        <th class="data-col">2</th>
                        <th class="data-col">1 DNB</th>
                        <th class="data-col">2 DNB</th>
                        <th class="data-col">1 DNB</th>
                        <th class="data-col">2 DNB</th>
                        <th class="data-col">1X</th>
                        <th class="data-col">X2</th>
                        <th class="data-col">12</th>
                        <th class="data-col">1X</th>
                        <th class="data-col">X2</th>
                        <th class="data-col">12</th>
                      </tr>
                    </thead>
                    <tbody>
                      <?php if (empty($matches)): ?>
                        <tr>
                          <td colspan="32" class="text-center py-5">
                            <i class="bx bx-info-circle" style="font-size: 3rem; color: #999;"></i>
                            <p class="mt-3 mb-0">No matches found for the selected filters.</p>
                            <small class="text-muted">Try adjusting your filter settings.</small>
                          </td>
                        </tr>
                      <?php else: ?>
                        <?php foreach ($matches as $match): ?>
                          <tr>
                            <td class="league-col"><?php echo htmlspecialchars($match['league']); ?></td>
                            <td class="date-col"><?php echo htmlspecialchars($match['date']); ?></td>
                            <td class="team-col"><?php echo htmlspecialchars($match['team1']); ?></td>
                            <td class="team-col"><?php echo htmlspecialchars($match['team2']); ?></td>

                            <!-- Half Time Bookmaker Odds -->
                            <td class="data-col"><?php echo htmlspecialchars($match['half_time']['bookmaker_odds']['1'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['half_time']['bookmaker_odds']['X'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['half_time']['bookmaker_odds']['2'] ?? '-'); ?></td>

                            <!-- Half Time Probability (ML PREDICTIONS!) -->
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['probability']['1'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['probability']['X'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['probability']['2'] ?? '-'); ?></td>

                            <!-- Half Time True Odds (CALCULATED FROM ML!) -->
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['true_odds']['1'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['true_odds']['X'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['half_time']['true_odds']['2'] ?? '-'); ?></td>

                            <!-- Full Time Bookmaker Odds -->
                            <td class="data-col"><?php echo htmlspecialchars($match['full_time']['bookmaker_odds']['1'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['full_time']['bookmaker_odds']['X'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['full_time']['bookmaker_odds']['2'] ?? '-'); ?></td>

                            <!-- Full Time Probability (ML PREDICTIONS!) -->
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['probability']['1'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['probability']['X'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['probability']['2'] ?? '-'); ?></td>

                            <!-- Full Time True Odds (CALCULATED FROM ML!) -->
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['true_odds']['1'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['true_odds']['X'] ?? '-'); ?></td>
                            <td class="data-col ml-prediction"><?php echo htmlspecialchars($match['full_time']['true_odds']['2'] ?? '-'); ?></td>

                            <!-- Draw No Bet (CALCULATED!) -->
                            <td class="data-col"><?php echo htmlspecialchars($match['draw_no_bet']['half_time']['1_dnb'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['draw_no_bet']['half_time']['2_dnb'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['draw_no_bet']['full_time']['1_dnb'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['draw_no_bet']['full_time']['2_dnb'] ?? '-'); ?></td>

                            <!-- Double Chance (CALCULATED!) -->
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['half_time']['1X'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['half_time']['X2'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['half_time']['12'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['full_time']['1X'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['full_time']['X2'] ?? '-'); ?></td>
                            <td class="data-col"><?php echo htmlspecialchars($match['double_chance']['full_time']['12'] ?? '-'); ?></td>
                          </tr>
                        <?php endforeach; ?>
                      <?php endif; ?>
                    </tbody>
                  </table>
                </div>

                <?php if (!empty($matches)): ?>
                <div class="mt-3">
                  <small class="text-muted">
                    <i class="bx bx-info-circle"></i>
                    <strong class="ml-prediction">Green values</strong> are ML predictions from
                    <?php
                    if (isset($matches[0]['models_used'])) {
                        echo implode(', ', array_map('ucfirst', $matches[0]['models_used']));
                    } else {
                        echo 'AI models';
                    }
                    ?>
                  </small>
                </div>
                <?php endif; ?>
              </div>
            </div>

          </div>
          <!-- / Content -->

<?php include 'includes/app-footer.php'; ?>
