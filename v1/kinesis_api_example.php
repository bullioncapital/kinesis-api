<?php

/*

Copyright 2022 Kinesis AG.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

- - - - - - - - - - - - - - - -

Notes:

* This file demostrates the basic usage of the Kinesis Public API.
* You will require a privateKey and publicKey from https://kms.kinesis.money/settings/api-keys
* Please note these are production endpoints and you are trading on your real account.

*/

$privateKey = 'your_private_key';
$publicKey  = 'your_access_token';

function getNonce() {

	$nonce = time() * 1000;
	return $nonce;
}

function getHeaders($method, $url, $content='') {

	global $privateKey;
	global $publicKey;

	$nonce   = getNonce();

	$message = $nonce . $method . $url . $content;

	$xsig    = strtoupper(hash_hmac('SHA256', $message, $privateKey));

	$authHeaders   = array();
	$authHeaders[] = "x-nonce: $nonce";
  	$authHeaders[] = "x-api-key: $publicKey";
	$authHeaders[] = "x-signature: $xsig";

	if ($method != 'DELETE')
	{
		$authHeaders[] = "Content-type: application/json";
	}

	return $authHeaders;
}

function callAPI($method, $api, $data='') {

    $url       = "https://client-api.kinesis.money" . $api;
    $curlParam = '';

    if ($method == 'GET' && !empty($data)){
    	$curlParam = '?' . http_build_query($data);
    }

    $headers  = getHeaders($method, $api);

    if ($method == 'POST') {
    	$data     = json_encode($data);
        $headers  = getHeaders($method, $api, $data);
   	}

    $curl     = curl_init($url . $curlParam);

    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);

    switch ($method) {
        case "GET":
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "GET");
            break;
        case "POST":
        	curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");
            break;
        case "PUT":
            curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "PUT");
            break;
        case "DELETE":
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "DELETE");
            break;
    }
    $response = curl_exec($curl);
    $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);

    curl_close($curl);

    // Check the HTTP Status code

    switch ($httpCode) {
        case 200:
        	$error_status = "200: Success";
            break;
        case 201:
        	$error_status = "201: Success";
            break;
        case 402:
            $error_status = "402: In sufficient funds";
            return ($error_status);
            break;
        case 403:
            $error_status = "403: Not authorised";
            return ($error_status);
            break;
        case 404:
            $error_status = "404: API Not found";
            return ($error_status);
            break;
        case 500:
            $error_status = "500: servers replied with an error.";
            return ($error_status);
            break;
        case 502:
            $error_status = "502: servers may be down or being upgraded. Hopefully they'll be OK soon!";
            return ($error_status);
            break;
        case 503:
            $error_status = "503: service unavailable. Hopefully they'll be OK soon!";
            return ($error_status);
            break;
        default:
            $error_status = "Undocumented error: " . $httpCode . " : " . curl_error($curl);
            return ($error_status);
            break;
    }
    return $response;
}


# ------------------------------
#  Get mid price example
# ------------------------------

echo "\n\nGet mid price\n\n";

$pair     = 'BTC_USD';
$url      = '/v1/exchange/mid-price/' . $pair;
$response = callAPI('GET', $url);

$prices   = json_decode($response);


# ------------------------------
#  Get holdings
# ------------------------------

echo "\n\nHoldings\n\n";

$url      = '/v1/exchange/holdings';
$response = callAPI('GET', $url);

echo($response);

# ------------------------------
#  Get available pairs
# ------------------------------

echo "\n\nGet pairs\n\n";

$url      = '/v1/exchange/pairs';
$response = callAPI('GET', $url);

echo($response);

# ------------------------------
#  Get available depth
# ------------------------------

echo "\n\nGet depth\n\n";

$pair     = 'KAU_USD';
$url      = '/v1/exchange/depth/' . $pair;
$response = callAPI('GET', $url);

echo($response);

# ------------------------------
#  Get OHLCV data
# ------------------------------

echo "\n\nGet OHLCV\n\n";

$pair     = 'KAU_USD';
$url      = '/v1/exchange/ohlc/' . $pair;
$params   = array(
	'fromDate'  => '2022-04-01T00:00:00.000Z',
	'toDate'    => '2022-04-15T00:00:00.000Z',
	'timeFrame' => 60
);
$response = callAPI('GET', $url, $params);

echo($response);

# ------------------------------
#  Place Buy and Sell orders
# ------------------------------

$pair     = 'KAU_USD';
$url      = '/v1/exchange/mid-price/' . $pair;
$response = callAPI('GET', $url);
$prices   = json_decode($response);

# Get the bid/ask for KAU to place limit orders above and below market

$askPrice = $prices->ask;
$bidPrice = $prices->bid;

echo "\n\nPlace a BUY order\n\n";

$url      = '/v1/exchange/orders';
$data   = array(
	'currencyPairId' => 'KAU_USD',
	'direction'      => 'buy',
	'amount'         => 0.05,
	'orderType'      => 'limit',
	'limitPrice'     => $askPrice - 2
);
$response = callAPI('POST', $url, $data);

echo($response);

echo "\n\nPlace a SELL order\n\n";

$url      = '/v1/exchange/orders';
$data   = array(
    'currencyPairId' => 'KAU_USD',
    'direction'      => 'sell',
    'amount'         => 0.05,
    'orderType'      => 'limit',
    'limitPrice'     => $bidPrice + 2
);
$response = callAPI('POST', $url, $data);

echo($response);

# ------------------------------
#  Get open orders
# ------------------------------

sleep(1);  # Give the order time tpo process

echo "\n\nGet open orders\n\n";

$url      = '/v1/exchange/orders/open';
$response = callAPI('GET', $url);
echo($response);

$openOrders = json_decode($response);

# ------------------------------
#  Cancel all open order
# ------------------------------

echo "\n\nCancel all open orders\n\n";

foreach($openOrders as $order) {
    $orderNo = $order->id;
    $url      = '/v1/exchange/orders/' . $orderNo;
    $response = callAPI('DELETE', $url);

    echo($response);
}

# ------------------------------
#  Get statement
# ------------------------------

echo "\n\nGet statement all symbols\n\n";

$url      = '/v1/exchange/reporting/account-balance-statement';
$response = callAPI('GET', $url);

echo($response);

echo "\n\nGet statement for LTC only\n\n";

$url      = '/v1/exchange/reporting/account-balance-statement/LTC';
$response = callAPI('GET', $url);

echo($response);

exit();

# ------------------------------
#  Send to email
# ------------------------------

echo "\n\nSend to email\n\n";

$receiverEmail  = 'your_email_address';
$currencyCode   = 'KAU';
$sendAmount     = 0.1;

$url    = '/v1/exchange/withdrawals/email';
$data   = array(
    'amount'        => $sendAmount,
    'currencyCode'  => $currencyCode,
    'receiverEmail' => $receiverEmail,
    'memo'          => 'Sent by API'
);
$response = callAPI('POST', $url, $data);

echo($response);

# ------------------------------
#  Send to wallet
# ------------------------------

echo "\n\nSend to wallet\n\n";

$receiveWallet  = 'kinesis_wallet_address_to_send_to';
$currencyCode   = 'KAU';
$sendAmount     = 0.05;

$url    = '/v1/exchange/withdrawals/address';
$data   = array(
    'amount'        => $sendAmount,
    'currencyCode'  => $currencyCode,
    'address'       => $receiveWallet,
    'memo'          => 'Sent to wallet'
);
$response = callAPI('POST', $url, $data);

echo($response);

exit();
