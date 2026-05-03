<?php
$method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
if ($method === 'OPTIONS') {
  header('Access-Control-Allow-Origin: *');
  header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type, Authorization');
  header('Access-Control-Max-Age: 86400');
  http_response_code(204);
  exit;
}

$scriptName = '/catalog/api-proxy.php';
$uri = $_SERVER['REQUEST_URI'] ?? '';
$path = parse_url($uri, PHP_URL_PATH) ?: '';
$pos = strpos($path, $scriptName);
if ($pos !== false) { $path = substr($path, $pos + strlen($scriptName)); }
if ($path === '' || $path === false) { $path = '/api/siteContext'; }
if (strpos($path, '/api/') !== 0) {
  http_response_code(400); header('Content-Type: application/json; charset=utf-8'); echo json_encode(['error'=>'Invalid API path']); exit;
}
$target = 'https://site-pro-api.nmarket.pro' . $path;
$q = $_SERVER['QUERY_STRING'] ?? '';
if ($q !== '') { $target .= '?' . $q; }
$headers = ['Accept: application/json', 'Origin: http://novostroy-market.allrealty.pro', 'Referer: http://novostroy-market.allrealty.pro/'];
$ct = $_SERVER['CONTENT_TYPE'] ?? '';
if ($ct !== '') { $headers[] = 'Content-Type: ' . $ct; }
$body = '';
if (in_array($method, ['POST','PUT','PATCH','DELETE'], true)) {
  $body = file_get_contents('php://input') ?: '';
}

$resp = false;
$status = 0;
$ctype = 'application/json; charset=utf-8';
$lastErr = '';

if (function_exists('curl_init')) {
  $ch = curl_init($target);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
  curl_setopt($ch, CURLOPT_TIMEOUT, 45);
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
  if ($body !== '') {
    curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
  }
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  $resp = curl_exec($ch);
  if ($resp === false) {
    $lastErr = curl_error($ch);
  } else {
    $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    $ctInfo = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
    if (is_string($ctInfo) && $ctInfo !== '') {
      $ctype = $ctInfo;
    }
  }
  curl_close($ch);
}

if ($resp === false) {
  $contextHeaders = "Accept: application/json\\r\\nOrigin: http://novostroy-market.allrealty.pro\\r\\nReferer: http://novostroy-market.allrealty.pro/\\r\\n";
  if ($ct !== '') {
    $contextHeaders .= "Content-Type: " . $ct . "\\r\\n";
  }
  $opts = [
    'http' => [
      'method' => $method,
      'header' => $contextHeaders,
      'content' => $body,
      'ignore_errors' => true,
      'timeout' => 45,
    ],
  ];
  $context = stream_context_create($opts);
  $resp = @file_get_contents($target, false, $context);
  $responseHeaders = $http_response_header ?? [];
  if (!empty($responseHeaders[0]) && preg_match('/\\s(\\d{3})\\s/', $responseHeaders[0], $m)) {
    $status = (int) $m[1];
  }
  foreach ($responseHeaders as $h) {
    if (stripos($h, 'Content-Type:') === 0) {
      $ctype = trim(substr($h, strlen('Content-Type:')));
      break;
    }
  }
}

if ($resp === false) {
  http_response_code(502);
  header('Access-Control-Allow-Origin: *');
  header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type, Authorization');
  header('Cache-Control: no-store');
  header('Content-Type: application/json; charset=utf-8');
  echo json_encode(['error'=>'Proxy failed','details'=>$lastErr ?: 'file_get_contents failed']);
  exit;
}

http_response_code($status ?: 200);
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Cache-Control: no-store');
header('Content-Type: ' . ($ctype ?: 'application/json; charset=utf-8'));
echo $resp;
