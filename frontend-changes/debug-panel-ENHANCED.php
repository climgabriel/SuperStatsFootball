<?php
/**
 * ENHANCED Debug Panel Component
 * Add these sections to your existing debug-panel.php
 */

// Add after line 370 (before closing </div> of debug-panel-body)
?>

        <!-- Cookies Section (NEW) -->
        <div class="debug-section">
            <div class="debug-section-title">🍪 Cookies</div>
            <div id="cookies-list" style="font-size: 10px; max-height: 100px; overflow-y: auto;">
                <?php
                $cookies = $_COOKIE;
                if (!empty($cookies)):
                    foreach ($cookies as $name => $value):
                        $displayValue = strlen($value) > 30 ? substr($value, 0, 30) . '...' : $value;
                ?>
                <div class="debug-item" style="margin: 2px 0;">
                    <span class="debug-label"><?php echo htmlspecialchars($name); ?>:</span>
                    <span class="debug-value" style="font-size: 9px;"><?php echo htmlspecialchars($displayValue); ?></span>
                </div>
                <?php
                    endforeach;
                else:
                ?>
                <div style="color: #999; padding: 5px;">No cookies set</div>
                <?php endif; ?>
            </div>
        </div>

        <!-- Request Headers Section (NEW) -->
        <div class="debug-section">
            <div class="debug-section-title">📤 Request Headers</div>
            <div style="font-size: 10px; max-height: 100px; overflow-y: auto;">
                <?php
                $headers = getallheaders();
                if ($headers):
                    foreach ($headers as $name => $value):
                        if (stripos($name, 'cookie') !== false || stripos($name, 'authorization') !== false) {
                            $value = substr($value, 0, 20) . '...';
                        }
                ?>
                <div class="debug-item" style="margin: 2px 0;">
                    <span class="debug-label"><?php echo htmlspecialchars($name); ?>:</span>
                    <span class="debug-value" style="font-size: 9px; word-break: break-all;"><?php echo htmlspecialchars($value); ?></span>
                </div>
                <?php
                    endforeach;
                endif;
                ?>
            </div>
        </div>

        <!-- Performance Metrics Section (NEW) -->
        <div class="debug-section">
            <div class="debug-section-title">⚡ Performance</div>
            <div class="debug-item">
                <span class="debug-label">Memory Usage:</span>
                <span class="debug-value"><?php echo round(memory_get_usage() / 1024 / 1024, 2); ?> MB</span>
            </div>
            <div class="debug-item">
                <span class="debug-label">Peak Memory:</span>
                <span class="debug-value"><?php echo round(memory_get_peak_usage() / 1024 / 1024, 2); ?> MB</span>
            </div>
            <div class="debug-item">
                <span class="debug-label">Loaded Files:</span>
                <span class="debug-value"><?php echo count(get_included_files()); ?> files</span>
            </div>
            <div class="debug-item">
                <span class="debug-label">Page Load Time:</span>
                <span class="debug-value" id="page-load-time">Calculating...</span>
            </div>
        </div>

        <!-- Session Data Section (NEW) -->
        <div class="debug-section">
            <div class="debug-section-title">💾 Session Data</div>
            <div style="font-size: 10px; max-height: 150px; overflow-y: auto;">
                <details>
                    <summary style="cursor: pointer; font-weight: bold; margin-bottom: 5px;">View Session Contents (<?php echo count($_SESSION); ?> items)</summary>
                    <pre style="margin: 5px 0; background: #f5f5f5; padding: 5px; border-radius: 3px; font-size: 9px; overflow-x: auto;"><?php
                        $sessionCopy = $_SESSION;
                        // Hide sensitive data
                        if (isset($sessionCopy[SESSION_TOKEN_KEY])) {
                            $sessionCopy[SESSION_TOKEN_KEY] = substr($sessionCopy[SESSION_TOKEN_KEY], 0, 20) . '...';
                        }
                        if (isset($sessionCopy['refresh_token'])) {
                            $sessionCopy['refresh_token'] = substr($sessionCopy['refresh_token'], 0, 20) . '...';
                        }
                        echo htmlspecialchars(json_encode($sessionCopy, JSON_PRETTY_PRINT));
                    ?></pre>
                </details>
            </div>
        </div>

        <!-- LocalStorage Section (NEW - populated by JavaScript) -->
        <div class="debug-section">
            <div class="debug-section-title">🗄️ LocalStorage</div>
            <div id="localstorage-list" style="font-size: 10px; max-height: 100px; overflow-y: auto;">
                <div style="color: #999; padding: 5px;">Loading...</div>
            </div>
        </div>

        <!-- Network Errors Log (NEW - populated by JavaScript) -->
        <div class="debug-section" id="network-errors-section" style="display:none;">
            <div class="debug-section-title">🚫 Network Errors</div>
            <div id="network-errors-list" style="font-size: 10px; max-height: 120px; overflow-y: auto;"></div>
        </div>

        <!-- Console Logs (NEW - populated by JavaScript) -->
        <div class="debug-section">
            <div class="debug-section-title">📝 Console Logs</div>
            <div id="console-logs-list" style="font-size: 10px; max-height: 120px; overflow-y: auto;">
                <div style="color: #999; padding: 5px;">Capturing console logs...</div>
            </div>
        </div>

<!-- Add these enhanced JavaScript functions before the closing </script> tag -->
<script>
// === ENHANCED LOGGING FEATURES ===

// Track network errors
const networkErrors = [];
function logNetworkError(error) {
    networkErrors.push({
        message: error.message || error.toString(),
        timestamp: new Date().toLocaleTimeString(),
        stack: error.stack
    });

    updateNetworkErrorsDisplay();
}

function updateNetworkErrorsDisplay() {
    const container = document.getElementById('network-errors-list');
    const section = document.getElementById('network-errors-section');

    if (networkErrors.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    container.innerHTML = networkErrors.map((error, index) => `
        <div style="padding: 5px; border-bottom: 1px solid #eee; background: #fff3cd;">
            <strong>#${networkErrors.length - index} - ${error.timestamp}</strong><br>
            <span style="color: #dc3545;">${error.message}</span>
            ${error.stack ? `<details style="margin-top: 3px;"><summary style="cursor: pointer; font-size: 9px;">Stack Trace</summary><pre style="font-size: 8px; margin: 2px 0; overflow-x: auto;">${error.stack}</pre></details>` : ''}
        </div>
    `).reverse().join('');
}

// Display LocalStorage contents
function updateLocalStorageDisplay() {
    const container = document.getElementById('localstorage-list');
    if (!container) return;

    const items = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        let value = localStorage.getItem(key);

        // Truncate long values
        if (value && value.length > 50) {
            value = value.substring(0, 50) + '...';
        }

        items.push({key, value});
    }

    if (items.length === 0) {
        container.innerHTML = '<div style="color: #999; padding: 5px;">No items in LocalStorage</div>';
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="debug-item" style="margin: 2px 0;">
            <span class="debug-label">${item.key}:</span>
            <span class="debug-value" style="font-size: 9px; word-break: break-all;">${item.value}</span>
        </div>
    `).join('');
}

// Capture console logs
const consoleLogs = [];
const originalConsoleLog = console.log;
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

console.log = function(...args) {
    consoleLogs.push({
        type: 'log',
        message: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '),
        timestamp: new Date().toLocaleTimeString()
    });
    updateConsoleLogsDisplay();
    originalConsoleLog.apply(console, args);
};

console.error = function(...args) {
    consoleLogs.push({
        type: 'error',
        message: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '),
        timestamp: new Date().toLocaleTimeString()
    });
    updateConsoleLogsDisplay();
    originalConsoleError.apply(console, args);
};

console.warn = function(...args) {
    consoleLogs.push({
        type: 'warn',
        message: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '),
        timestamp: new Date().toLocaleTimeString()
    });
    updateConsoleLogsDisplay();
    originalConsoleWarn.apply(console, args);
};

function updateConsoleLogsDisplay() {
    const container = document.getElementById('console-logs-list');
    if (!container) return;

    if (consoleLogs.length === 0) {
        container.innerHTML = '<div style="color: #999; padding: 5px;">No console logs yet</div>';
        return;
    }

    // Keep last 10 logs
    const recentLogs = consoleLogs.slice(-10);

    container.innerHTML = recentLogs.map((log, index) => {
        const bgColor = log.type === 'error' ? '#fff3cd' :
                       log.type === 'warn' ? '#fff9e6' :
                       '#f5f5f5';
        const textColor = log.type === 'error' ? '#dc3545' :
                         log.type === 'warn' ? '#ff9800' :
                         '#333';

        return `
            <div style="padding: 4px; border-bottom: 1px solid #eee; background: ${bgColor};">
                <div style="display: flex; justify-content: space-between; font-size: 9px;">
                    <span style="color: ${textColor}; font-weight: bold;">${log.type.toUpperCase()}</span>
                    <span style="color: #999;">${log.timestamp}</span>
                </div>
                <div style="color: ${textColor}; font-size: 9px; margin-top: 2px; word-break: break-word;">${log.message}</div>
            </div>
        `;
    }).reverse().join('');
}

// Calculate page load time
window.addEventListener('load', function() {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    const loadTimeElement = document.getElementById('page-load-time');
    if (loadTimeElement) {
        loadTimeElement.textContent = (loadTime / 1000).toFixed(3) + ' seconds';
    }
});

// Update LocalStorage on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    updateLocalStorageDisplay();

    // Refresh LocalStorage display every 5 seconds
    setInterval(updateLocalStorageDisplay, 5000);

    console.log('🔧 Enhanced Debug Panel loaded');
});

// Enhanced error tracking
window.addEventListener('error', function(event) {
    logNetworkError({
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
    });
});

// Unhandled promise rejection tracking
window.addEventListener('unhandledrejection', function(event) {
    logNetworkError({
        message: 'Unhandled Promise Rejection: ' + event.reason,
        stack: event.reason?.stack
    });
});

// Export function to get all debug data programmatically
window.getFullDebugReport = function() {
    return {
        consoleLogs: consoleLogs,
        networkErrors: networkErrors,
        apiCalls: window.debugGetApiCalls ? window.debugGetApiCalls() : [],
        localStorage: Object.fromEntries(
            Array.from({length: localStorage.length}, (_, i) => {
                const key = localStorage.key(i);
                return [key, localStorage.getItem(key)];
            })
        ),
        sessionStorage: Object.fromEntries(
            Array.from({length: sessionStorage.length}, (_, i) => {
                const key = sessionStorage.key(i);
                return [key, sessionStorage.getItem(key)];
            })
        ),
        performance: {
            loadTime: (performance.timing.loadEventEnd - performance.timing.navigationStart) / 1000,
            domReady: (performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart) / 1000,
            firstPaint: performance.getEntriesByType('paint').find(e => e.name === 'first-paint')?.startTime / 1000
        }
    };
};

// Enhanced copy function with all new data
function copyEnhancedDebugInfo(event) {
    event.stopPropagation();

    const fullReport = window.getFullDebugReport();
    let debugInfo = `=== ENHANCED Super Stats Football - Debug Report ===
Generated: ${new Date().toLocaleString()}
Page: ${document.title}
URL: ${window.location.href}

`;

    // Add all existing sections from original copyAllDebugInfo()...
    // (Keep your existing code)

    // Add new enhanced sections
    debugInfo += `🍪 COOKIES (${Object.keys(document.cookie.split(';')).length})
`;
    document.cookie.split(';').forEach(cookie => {
        const [name, value] = cookie.split('=').map(s => s.trim());
        debugInfo += `${name}: ${value?.substring(0, 30)}...
`;
    });
    debugInfo += `

`;

    debugInfo += `🗄️ LOCALSTORAGE (${Object.keys(fullReport.localStorage).length} items)
`;
    Object.entries(fullReport.localStorage).forEach(([key, value]) => {
        debugInfo += `${key}: ${value?.substring(0, 50)}${value?.length > 50 ? '...' : ''}
`;
    });
    debugInfo += `

`;

    debugInfo += `⚡ PERFORMANCE METRICS
`;
    debugInfo += `Page Load Time: ${fullReport.performance.loadTime?.toFixed(3)}s
`;
    debugInfo += `DOM Ready: ${fullReport.performance.domReady?.toFixed(3)}s
`;
    debugInfo += `First Paint: ${fullReport.performance.firstPaint?.toFixed(3)}s
`;
    debugInfo += `

`;

    debugInfo += `📝 CONSOLE LOGS (Last ${Math.min(consoleLogs.length, 10)})
`;
    consoleLogs.slice(-10).forEach((log, index) => {
        debugInfo += `[${log.timestamp}] ${log.type.toUpperCase()}: ${log.message}
`;
    });
    debugInfo += `

`;

    if (networkErrors.length > 0) {
        debugInfo += `🚫 NETWORK ERRORS (${networkErrors.length})
`;
        networkErrors.forEach((error, index) => {
            debugInfo += `#${index + 1} [${error.timestamp}] ${error.message}
`;
        });
        debugInfo += `

`;
    }

    navigator.clipboard.writeText(debugInfo).then(() => {
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Enhanced Copy!';
        btn.style.background = '#28a745';

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '#106147';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Copy failed. Check console.');
    });
}
</script>
