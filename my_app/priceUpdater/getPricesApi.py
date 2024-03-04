import sys
sys.path.append("..")
import requests
from datetime import datetime
import json
from django.utils import timezone
from decimal import Decimal

def func():
    print("func started...")
    from my_app.models import Coin, CustomUser

    # track the number of times this function has been run
    func_run_count = 0

    """ on the first run of the app and every 1000th run of the app:
            1. fetch the top 100 coins.
            2. for each fetched coin:
                    If the fetched coin is not in the database:
                        add it to the database """
    
    if (func_run_count % 1000 == 0):
        func_run_count = func_run_count + 1
        url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=aud&order=market_cap_desc&per_page=100&page=1&sparkline=false&locale=en&x_cg_demo_api_key=CG-JPtjy3AuuzkAk31PNjSnUfUC' 
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
        
        # for each fetched coin:
        for coin in data:

                # save the coin into our database.if it's not
                # already there
                print("checking if coin with symbol ", coin['symbol'], " is in the database")
                existing_coin = Coin.objects.filter(symbol=coin['symbol']).exists()

                if (not existing_coin):
                    new_coin =  Coin(id= coin['id'],
                                symbol= coin['symbol'],
                                name= coin['name'],
                                image_url=coin['image'],
                                price=coin['current_price'],
                                market_cap=coin['market_cap'],
                                volume=coin['total_volume'],
                                high_24h=coin['high_24h'],
                                low_24h=coin['low_24h'],
                                change_24h=coin['price_change_24h'],
                                percent_change_24h=coin['price_change_percentage_24h'])
                    new_coin.save()

    """ on every run of the app:
        1. fetch data on every coin in the database
        2. For each fetched coin:
            update its entry in the database """
    
    base_url = 'https://api.coingecko.com/api/v3/coins/markets'

    # Get a list of every coin in the databsae
    ids_list = Coin.objects.all().values_list('id', flat=True)

    params = {
        'vs_currency': "aud",
        'ids': ','.join(ids_list),  # Join the list elements with commas
        'order': 'market_cap_desc',  # Order by market cap descending
        'per_page': len(ids_list),  # Set per_page to the number of coins in the list
        'page': 1,
        'sparkline': False,
    }

    print('printing joined ids list ', ','.join(ids_list))
    print('length of ids list is ', len(ids_list))

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
    
    print('printing data ', data)

    # For each fetched coin:
    for coin in data:
        # find coin in database
        print("updating coin with symbol ", coin['symbol'])
        existing_coin = Coin.objects.get(symbol=coin['symbol'])

        # update database entry for this coin
        existing_coin.price = coin['current_price']
        existing_coin.market_cap = coin['market_cap']
        existing_coin.volume=coin['total_volume']
        existing_coin.high_24h=coin['high_24h']
        existing_coin.low_24h=coin['low_24h']
        existing_coin.change_24h=coin['price_change_24h']
        existing_coin.percent_change_24h=coin['price_change_percentage_24h']

        # update coin's graph
        coin_graph_dict = json.loads(existing_coin.graph)
        coin_graph_dict["date"].append(str(datetime.now()))
        coin_graph_dict["value"].append(float(existing_coin.price))
        existing_coin.graph = json.dumps(coin_graph_dict)

        # save changes to database
        existing_coin.save()
    
    # for each user:
    for user in CustomUser.objects.all():
        # reset the user's portfolio value to 0
        user.portfolio_value = Decimal(0)

        # for each coin in the user's portfolio:
        for coin_in_dict in user.portfolio_dict:
            # find the coin in the database
            coin_in_database = Coin.objects.get(symbol=coin_in_dict)

            # update the user's portfolio value
            user.portfolio_value += (coin_in_database.price * Decimal(user.portfolio_dict[coin_in_dict]))

        # save the updated user's portfolio value
        user.save()

    # everyone's portfolio value has been updated, so push portfolio values
    # to the portfolio graph for each user
    for user in CustomUser.objects.all():
        # convert user.portfolio_graph back into a python dictionary

        # update date and value lists in the json
        portfolio_graph_dict = json.loads(user.portfolio_graph)
        portfolio_graph_dict["date"].append(str(datetime.now()))
        portfolio_graph_dict["value"].append(float(user.portfolio_value))
        user.portfolio_graph = json.dumps(portfolio_graph_dict)

        # convert back to json, save in user.portfolio_graph
        user.save()

    print("database updated.")