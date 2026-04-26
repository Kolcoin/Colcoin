<?php
declare(strict_types=1);

header('Content-Type: text/plain; charset=UTF-8');

$sourceUrl = 'https://raw.githubusercontent.com/Kolcoin/Colcoin/cursor/tushino-100-pages-cd0d/starts/nmarket-85433.html';
$targetDir = __DIR__ . '/starts';
$targetFile = $targetDir . '/nmarket-85433.html';

function fetchRemote(string $url): string {
    $attempts = 4;
    $lastError = 'unknown error';

    for ($i = 1; $i <= $attempts; $i++) {
        if (function_exists('curl_init')) {
            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_CONNECTTIMEOUT => 10,
                CURLOPT_TIMEOUT => 30,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,
                CURLOPT_USERAGENT => 'ShmitrixFixer/1.0',
            ]);
            $body = curl_exec($ch);
            $err = curl_error($ch);
            $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($body !== false && $code >= 200 && $code < 300) {
                return (string)$body;
            }
            $lastError = 'cURL HTTP ' . $code . ($err ? ' / ' . $err : '');
        } else {
            $context = stream_context_create([
                'http' => ['timeout' => 30, 'header' => "User-Agent: ShmitrixFixer/1.0\r\n"],
                'ssl' => ['verify_peer' => false, 'verify_peer_name' => false],
            ]);
            $body = @file_get_contents($url, false, $context);
            if ($body !== false && strlen($body) > 1000) {
                return (string)$body;
            }
            $lastError = 'file_get_contents failed';
        }

        usleep(300000 * $i);
    }

    throw new RuntimeException('Cannot fetch source: ' . $lastError);
}

try {
    if (!is_dir($targetDir) && !mkdir($targetDir, 0755, true) && !is_dir($targetDir)) {
        throw new RuntimeException('Cannot create target dir: ' . $targetDir);
    }

    $html = fetchRemote($sourceUrl);
    $html = str_replace("\r\n", "\n", $html);

    if (stripos($html, '<!DOCTYPE html>') === false || mb_stripos($html, 'ЖК 1-й Донской', 0, 'UTF-8') === false) {
        throw new RuntimeException('Validation failed: unexpected source content');
    }

    $bytes = file_put_contents($targetFile, $html, LOCK_EX);
    if ($bytes === false) {
        throw new RuntimeException('Cannot write file: ' . $targetFile);
    }

    @chmod($targetFile, 0644);
    clearstatcache(true, $targetFile);

    echo "OK\n";
    echo "Written: {$bytes} bytes\n";
    echo "Target: {$targetFile}\n";
    echo "Source: {$sourceUrl}\n";
    echo "Now open: https://xn--h1aagfvid9b.xn--p1ai/starts/nmarket-85433.html?v=" . time() . "\n";
} catch (Throwable $e) {
    http_response_code(500);
    echo "ERROR\n";
    echo $e->getMessage() . "\n";
}
