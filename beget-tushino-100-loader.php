<?php
header('Content-Type: text/plain; charset=utf-8');
set_time_limit(0);

function fetch_url($url, $retries = 4) {
    for ($i = 0; $i < $retries; $i++) {
        if (function_exists('curl_init')) {
            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_CONNECTTIMEOUT => 20,
                CURLOPT_TIMEOUT => 90,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => 0,
                CURLOPT_USERAGENT => 'Mozilla/5.0 (Tushino100Loader)'
            ]);
            $data = curl_exec($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            if ($data !== false && $code >= 200 && $code < 300) {
                return $data;
            }
        } else {
            $ctx = stream_context_create([
                'http' => [
                    'timeout' => 90,
                    'header' => "User-Agent: Mozilla/5.0 (Tushino100Loader)\r\n"
                ],
                'ssl' => [
                    'verify_peer' => false,
                    'verify_peer_name' => false
                ]
            ]);
            $data = @file_get_contents($url, false, $ctx);
            if ($data !== false && strlen($data) > 0) {
                return $data;
            }
        }
        sleep(2 + $i);
    }
    return null;
}

$branch = 'cursor/tushino-100-pages-cd0d';
$root = __DIR__;
$seo = $root . '/seo';
if (!is_dir($seo)) {
    mkdir($seo, 0755, true);
}

$rootFiles = ['blog.html', 'sitemap.xml', 'sitemap-tushino-100.xml'];
foreach ($rootFiles as $rf) {
    $data = fetch_url('https://raw.githubusercontent.com/Kolcoin/Colcoin/' . $branch . '/' . $rf);
    if ($data) {
        file_put_contents($root . '/' . $rf, $data);
        echo "OK root: $rf\n";
    } else {
        echo "FAIL root: $rf\n";
    }
}

$list = fetch_url('https://raw.githubusercontent.com/Kolcoin/Colcoin/' . $branch . '/seo-tushino-100-urls.txt');
if (!$list) {
    echo "FAIL list\n";
    exit;
}

$lines = preg_split('/\r\n|\r|\n/', $list);
$total = 0;
$ok = 0;
$fail = 0;
foreach ($lines as $u) {
    $u = trim($u);
    if (!$u || strpos($u, '/seo/') === false) {
        continue;
    }
    $file = basename(parse_url($u, PHP_URL_PATH));
    if (!$file || substr($file, -5) !== '.html') {
        continue;
    }
    $raw = 'https://raw.githubusercontent.com/Kolcoin/Colcoin/' . $branch . '/seo/' . $file;
    $html = fetch_url($raw);
    $total++;
    if (!$html || stripos($html, '<html') === false) {
        echo "FAIL page: $file\n";
        $fail++;
        continue;
    }
    file_put_contents($seo . '/' . $file, $html);
    echo "OK page: $file\n";
    $ok++;
}

$promptUrl = 'https://raw.githubusercontent.com/Kolcoin/Colcoin/' . $branch . '/saved-prompts/prompt-obyavlenie-kvartiry-msk-tushino.txt';
$prompt = fetch_url($promptUrl);
if ($prompt) {
    if (!is_dir($root . '/saved-prompts')) {
        mkdir($root . '/saved-prompts', 0755, true);
    }
    file_put_contents($root . '/saved-prompts/prompt-obyavlenie-kvartiry-msk-tushino.txt', $prompt);
    echo "OK prompt\n";
} else {
    echo "FAIL prompt\n";
}

echo "=== RESULT ===\n";
echo "Total pages: $total\n";
echo "Saved: $ok\n";
echo "Failed: $fail\n";
echo "Done.\n";
?>
