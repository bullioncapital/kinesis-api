"""

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

"""

import requests
import time
import pandas as pd
from   datetime import timezone
import datetime
import hmac
import hashlib
import html
import json


"""
Global variables
"""

privateKey = 'your_private_key'
publicKey  = 'your_access_token'
base_url   = 'https://client-api.kinesis.money'

sendAmount = 0.05
sendToken  = 'KAU'
sendEmail  = 'email_to_send_to'
sendWallet = 'kinesis_wallet_address_to_send_to'

def separator():
    print ()
    print ('=====')
    print ()

def getNonce ():

    dt            = datetime.datetime.now(timezone.utc)
    utc_time      = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = round(utc_time.timestamp() * 1000)

    return str(utc_timestamp)

def getAuthHeader(method, url, content=''):

    nonce    = getNonce()
    message  = str(nonce) + str(method) + str(url) + str(content)
    message  = message.encode(encoding='UTF-8',errors='strict')

    byte_key = bytes(privateKey, 'UTF-8')
    xsig     = hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()

    headers = {
            "x-nonce": nonce,
            "x-api-key": publicKey,
            "x-signature": xsig
            }

    if method != 'DELETE':
        headers["Content-Type"] = "application/json"

    return headers

def cancelOrder(orderNo):

    url = "/v1/exchange/orders/" + orderNo
    headersAuth = getAuthHeader('DELETE', url)

    try:
        response = requests.delete(base_url + url, headers = headersAuth)

    except:
        return response

    return response

def placeOrder(symbol, orderDirection, orderAmount, OrderType, priceLimit=0):

    url     = '/v1/exchange/orders'
    payload =  {
        'currencyPairId': symbol,
        'direction': orderDirection,
        'amount': float(orderAmount),
        'orderType': OrderType,
        'limitPrice': priceLimit
        }
    payload = json.dumps(payload, separators=(',', ':'))

    print(payload)

    headersAuth = getAuthHeader('POST', url, payload)

    print(payload)

    orderToCancel = ''

    try:
        response  = requests.post(base_url + url, data=payload, headers=headersAuth)
        print (response)

        try:
            arr = response.json()
            print (arr)
            print (response.status_code)

            if response.status_code != 402:

                orderToCancel = arr["id"]
                return orderToCancel
        except:
            return response

    except requests.exceptions.RequestException as err:
        print ("Oops: something Else",err)
    except requests.exceptions.HTTPError as errh:
        print ("Http error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout error:",errt)

    return response

def getHoldings():

    url         = '/v1/exchange/holdings'
    headersAuth = getAuthHeader('GET', url)

    try:
        response = requests.get(base_url + url, headers=headersAuth)

    except:
        return response

    return response

def getPairs():

    url         = '/v1/exchange/pairs'
    headersAuth = getAuthHeader('GET',url)

    try:
        response = requests.get(base_url + url, headers=headersAuth)
    except:
        return response

    return response

def getDepth(pair):

    url         = '/v1/exchange/depth/' + pair
    headersAuth = getAuthHeader('GET',url)

    try:
        response = requests.get(base_url + url, headers=headersAuth)
    except:
        return response

    return response

def getOHLC(pair, fromDate='2022-01-01T00:00:00.000Z', toDate='2022-03-31T00:00:00.000Z', timeFrame='60'):

    url         = '/v1/exchange/ohlc/' + pair
    headersAuth = getAuthHeader('GET', url)
    payload     = {'timeFrame': timeFrame,
            'fromDate': fromDate,
            'toDate': toDate
        }

    try:
        response = requests.get(base_url + url, headers=headersAuth, params=payload)

    except:
        return response

    return response

def getPrice(pair):

    url         = '/v1/exchange/mid-price/' + pair
    headersAuth = getAuthHeader('GET',url)

    try:
        response  = requests.get(base_url + url, headers=headersAuth)
    except:
        return response

    return response

def getStatement(pair=''):

    if not pair:
        url  = '/v1/exchange/reporting/account-balance-statement/' + pair
    else:
        url  = '/v1/exchange/reporting/account-balance-statement'

    headersAuth = getAuthHeader('GET',url)

    try:
        response  = requests.get(base_url + url, headers=headersAuth)
    except:
        return response

    return response

def getOpenOrders():

    url = '/v1/exchange/orders/open'
    headersAuth = getAuthHeader('GET', url)

    try:
        response = requests.get(base_url + url, headers=headersAuth)
    except:
        return response

    return response

def sendToWallet(sendAmount, pair, wallet, memo='Send to wallet'):

    url     = '/v1/exchange/withdrawals/address'
    payload =  {
        'amount': sendAmount,
        'currencyCode': pair,
        'address': wallet,
        'memo': memo
        }
    payload     = json.dumps(payload, separators=(',', ':'))
    headersAuth = getAuthHeader('POST', url, payload)

    print(url)
    print(headersAuth)
    print(payload)

    response  = requests.post(base_url + url, data=payload, headers=headersAuth)

    return response


def sendToEmail(sendAmount, pair, email, description='Send to email'):
    url     = '/v1/exchange/withdrawals/email'
    payload =  {
        'amount': sendAmount,
        'currencyCode': pair,
        'receiverEmail': email,
        'description': description
        }
    payload     = json.dumps(payload, separators=(',', ':'))
    headersAuth = getAuthHeader('POST', url, payload)

    print(url)
    print(headersAuth)
    print(payload)

    response    = requests.post(base_url + url, data=payload, headers=headersAuth)

    return response

def bidAskCheck(Symbol):
    today     = datetime.datetime.now(timezone.utc)
    price     = getPrice(Symbol).json()
    ask_price = price["ask"]
    bid_price = price["bid"]

    if bid_price > ask_price:
        print(str(today) + ' ' + Symbol + ' bid: ' + str(bid_price) + ' ask: ' + str(ask_price))
    time.sleep(5)

"""
Main app
"""

def main():


    print ('Started')

    try:
        holdings = getHoldings().json()
        print (pd.DataFrame(holdings))
    except:
        print('Unable to get holdings')
    separator()

    try:
        pairs = getPairs().json()
        print (pd.DataFrame(pairs))
    except:
        print('Unable to get pairs')
    separator()

    try:
        depth = getDepth('KAU_USD').json()
        df    = pd.DataFrame(depth)

        print ('Bid depth for KAU_USD')
        print (pd.DataFrame(df["depthItems"]["bid"]))
        separator()
        print ('Ask depth for KAU_USD')
        print (pd.DataFrame(df["depthItems"]["ask"]))
    except:
        print('unable to get depth')
    separator()


    try:
        today    = datetime.datetime.now(timezone.utc)
        daysAgo  = datetime.timedelta(days = 5)
        fromDate = today - daysAgo
        fromDate = fromDate.isoformat().replace('+00:00', 'Z')
        toDate   = today.isoformat().replace('+00:00', 'Z')


        ohlc = getOHLC('KAU_USD',fromDate,toDate,60).json()
        df   = pd.DataFrame(ohlc)
        print(df)
    except:
        print('Unable to get OHLC')

    separator()

    try:
        price     = getPrice('KAU_USD').json()
        mid_price = round(price["mid_price"],4)
        ask_price = price["ask"]
        bid_price = price["bid"]

        print ("KAU mid prices is " + str(mid_price))
        print ("KAU bid prices is " + str(bid_price))
        print ("KAU ask prices is " + str(ask_price))
    except:
        print('Unable to get mid price')
    separator()

    try:
        response = getStatement('LTC')
        statement = response.json()
        df = pd.DataFrame(statement)
        print(df)
    except:
        print('Unable to get statement')

    separator()


    """
    Place single order and cancel
    """

    orderToCancel = placeOrder('KAU_USD', 'buy', 0.01 , 'limit', bid_price - 2)
    print("Just placed order " + orderToCancel)

    time.sleep(2)

    print ('Cancelling ' + orderToCancel)
    cancelOrder(orderToCancel)

    separator()

    placeOrder('KAU_USD', 'sell', 0.01, 'limit', ask_price + 2)
    placeOrder('KAU_USD', 'buy', 100, 'limit', bid_price - 2)
    placeOrder('KAG_USD', 'buy', 0.05, 'limit', 24)

    time.sleep(10)

    separator()

    """
    Get all the open orders
    """
    try:
        orders = getOpenOrders().json()

        for order in orders:
            print ('Cancelling: ' + order['id'])
            cancelOrder(order['id'])
            time.sleep(1)
        print ()
        print ("All open orders cancelled.")
    except:
        print('Unable to get orders')
    separator()

    """
    Send to email and wallet
    """

    exit()

    sendTo = sendToEmail(sendAmount, sendToken, sendEmail, 'email')

    if sendTo.status_code == 201:
        print ('Transfer completed')
    else:
        print (sendTo)
        print( 'An error occurred during the transfer')

    separator()

    sendTo = sendToWallet(sendAmount, sendToken, sendWallet, 'wallet')

    if sendTo.status_code == 201:
        print ('Transfer completed')
    else:
        print (sendTo)
        print( 'An error occurred during the transfer')

    separator()

    exit()

if __name__ == "__main__":
    main()
