<?php
error_reporting(0);
ini_set('display_errors', '0');

$method = isset($_SERVER['REQUEST_METHOD']) ? strtoupper($_SERVER['REQUEST_METHOD']) : 'GET';

if ($method === 'OPTIONS') {
  header('Access-Control-Allow-Origin: *');
  header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type, Authorization');
  header('Access-Control-Max-Age: 86400');
  http_response_code(204);
  exit;
}

$uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
$path = parse_url($uri, PHP_URL_PATH);
if (!$path) { $path = ''; }

$scriptName = '/catalog/api-proxy.php';
$pos = strpos($path, $scriptName);
if ($pos !== false) {
  $path = substr($path, $pos + strlen($scriptName));
}

if ($path === '' || $path === false) {
  $path = '/api/siteContext';
}

if (strpos($path, '/api/') !== 0) {
  http_response_code(400);
  header('Access-Control-Allow-Origin: *');
  header('Content-Type: application/json; charset=utf-8');
  echo json_encode(array('error' => 'Invalid API path', 'path' => $path));
  exit;
}

$target = 'https://site-pro-api.nmarket.pro' . $path;
$query = isset($_SERVER['QUERY_STRING']) ? $_SERVER['QUERY_STRING'] : '';
if ($query !== '') {
  $target .= '?' . $query;
}

$contentType = isset($_SERVER['CONTENT_TYPE']) ? $_SERVER['CONTENT_TYPE'] : '';
$body = '';
if (in_array($method, array('POST','PUT','PATCH','DELETE'), true)) {
  $raw = file_get_contents('php://input');
  if ($raw !== false) { $body = $raw; }
}

$responseBody = false;
$responseCode = 0;
$responseType = 'application/json; charset=utf-8';
$lastError = '';

if (function_exists('curl_init')) {
  $headers = array(
    'Accept: application/json',
    'Origin: http://novostroy-market.allrealty.pro',
    'Referer: http://novostroy-market.allrealty.pro/'
  );
  if ($contentType !== '') {
    $headers[] = 'Content-Type: ' . $contentType;
  }

  $ch = curl_init($target);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
  curl_setopt($ch, CURLOPT_TIMEOUT, 45);
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  if ($body !== '') {
    curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
  }

  $execResult = curl_exec($ch);
  if ($execResult !== false) {
    $responseBody = $execResult;
    $responseCode = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    $ctInfo = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
    if (is_string($ctInfo) && $ctInfo !== '') {
      $responseType = $ctInfo;
    }
  } else {
    $lastError = curl_error($ch);
  }
  curl_close($ch);
}

if ($responseBody === false) {
  $headerLines = "Accept: application/json\r\n" .
                 "Origin: http://novostroy-market.allrealty.pro\r\n" .
                 "Referer: http://novostroy-market.allrealty.pro/\r\n";
  if ($contentType !== '') {
    $headerLines .= 'Content-Type: ' . $contentType . "\r\n";
  }

  $opts = array(
    'http' => array(
      'method' => $method,
      'header' => $headerLines,
      'ignore_errors' => true,
      'timeout' => 45,
      'content' => $body
    )
  );

  $context = stream_context_create($opts);
  $fgc = @file_get_contents($target, false, $context);

  if ($fgc !== false) {
    $responseBody = $fgc;
    if (isset($http_response_header) && is_array($http_response_header)) {
      if (!empty($http_response_header[0]) && preg_match('/\s(\d{3})\s/', $http_response_header[0], $m)) {
        $responseCode = (int)$m[1];
      }
      foreach ($http_response_header as $h) {
        if (stripos($h, 'Content-Type:') === 0) {
          $responseType = trim(substr($h, strlen('Content-Type:')));
          break;
        }
      }
    }
  } else {
    if ($lastError === '') {
      $lastError = 'file_get_contents failed';
    }
  }
}

if ($responseBody === false) {
  http_response_code(502);
  header('Access-Control-Allow-Origin: *');
  header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
  header('Access-Control-Allow-Headers: Content-Type, Authorization');
  header('Cache-Control: no-store');
  header('Content-Type: application/json; charset=utf-8');
  echo json_encode(array('error' => 'Proxy failed', 'details' => $lastError));
  exit;
}

http_response_code($responseCode > 0 ? $responseCode : 200);
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Cache-Control: no-store');
header('Content-Type: ' . $responseType);
echo $responseBody;
