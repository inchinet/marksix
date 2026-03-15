<?php
/**
 * Author-only Sync Trigger
 * This script runs the Python data sync when called by the HTML.
 */

// Simple security: You can add an IP check here if you want
// if ($_SERVER['REMOTE_ADDR'] !== 'YOUR_IP_ADDRESS') { die('Unauthorized'); }

header('Content-Type: application/json');

// Run the python script and capture output
$command = 'Z:\\antigravity\\venv\\Scripts\\python.exe sync_data_suggestion.py';
$output = shell_exec($command . ' 2>&1');

echo json_encode([
    'status' => 'success',
    'message' => 'Sync completed',
    'details' => $output,
    'time' => date('Y-m-d H:i:s')
]);
?>
