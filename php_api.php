<?php
header('Content-Type: application/json');
echo json_encode([
    "message" => "Hello from PHP API!",
    "timestamp" => microtime(true),
    "language" => "PHP"
]);
?> 