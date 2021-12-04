import sys,os
# Gives file access to parent directory and direct imports from there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
from api_bridge.binance_exchange import ExchangeBridge
from globals_client import client
import asyncio
import time




class UpdateLiveCandidates(object):
    '''Putting a series of methods into one class so I can asynchronously perform them and use the setattr() method'''
    def __init__(self):
        #Create binance client object:
        self.client = ExchangeBridge().return_client()
        self.async_tasks = []
        self.delisted_coins = ['BCCBTC', 'HSRBTC', 'ICNETH', 'SALTBTC', 'SALTETH', 'SUBBTC', 'SUBETH', 'ICNBTC', 'HSRETH', 'MODBTC', 'MODETH', 'VENBNB', 'VENBTC', 
        'VENETH', 'BCCETH', 'BCCUSDT', 'BCCBNB', 'WINGSBTC', 'WINGSETH', 'TRIGBTC', 'TRIGETH', 'TRIGBNB', 'CHATBTC', 'CHATETH', 'RPXBTC', 'RPXETH', 'RPXBNB', 
        'CLOAKBTC', 'CLOAKETH', 'BCNBTC', 'BCNETH', 'BCNBNB', 'TUSDBTC', 'TUSDETH', 'TUSDBNB', 'VENUSDT', 'PHXBTC', 'PHXETH', 'PHXBNB', 'PAXBTC', 'PAXBNB', 
        'PAXETH', 'USDCBNB', 'USDCBTC', 'BCHSVBTC', 'BCHSVUSDT', 'BCHSVTUSD', 'BCHSVPAX', 'BCHSVUSDC']


    async def sort_volume(self,coin):
        try:
            return {"symbol":coin,"volume":float(self.client.get_historical_klines(symbol=coin,interval="1d",start_str="1 Day Ago UTC")[0][7])}
        except IndexError:
            # The symbol is probably new to the exchange and doesnt have enough historical data or it has been taken off the exchange
            print("IndexError for "+coin)
            return {"symbol":coin,"volume":0}


    async def sort_symbols(self,symbols):
        for symbol in symbols:
            temp_task = self.loop.create_task(self.sort_volume(symbol))
            setattr(self,f"self.{symbol}",temp_task)
            del temp_task
            self.async_tasks.append(getattr(self,f"self.{symbol}"))
        #Very important step:
        await asyncio.wait(self.async_tasks)
            

    def update_live_candidates(self,symbols_excluded=[]):
        try:
            self.loop = asyncio.get_event_loop()
            symbols = ExchangeBridge().get_24hour_ticker(base_asset=False)
            symbols = [i for i in symbols if i not in self.delisted_coins]
            self.loop.run_until_complete(self.sort_symbols(symbols))
            #Convert result objects to regular results:
            self.async_tasks = [i.result() for i in self.async_tasks]
            return self.order_symbols(self.async_tasks)
        except Exception as e:
            print("Error: "+str(e))
        finally:
            self.loop.close()

        
    def order_symbols(self,values):
        ''''''
        #NOTE: symbols to scan: must be over 1000 BTC or over 8000 ETH (5000 if the market is a little dry) or over 13000 BNB
        #Take all symbols out that dont meet volume requirments:
        for i in values:
            # print(i["symbol"])
            if "PAX" in i["symbol"] or "USDC" in i["symbol"] or "USDT" in i["symbol"]:
                values.remove(i)
            if "BTC" in i["symbol"]:
                if i["volume"] < 1000:
                    values.remove(i)
            elif "ETH" in i["symbol"]:
                if i["volume"] < 5000:
                    values.remove(i)
            elif "BNB" in i["symbol"]:
                if i["volume"] < 13000:
                    values.remove(i)
        #Return a sorted array of the remaining values
        return [i["symbol"] for i in sorted(values, key=lambda k: k['volume'])]




#NOTE: This usually takes about 3-3.5 minutes to complete
def update_candidates():
    '''Retreives the markets with the most volume and updates the global vars server with them through live_candidates'''
    #Initiate updater object
    updater = UpdateLiveCandidates()
    while True:
        #Retreive updated list 
        updated_symbols = updater.update_live_candidates()
        #Update live_candidates in global vars server
        try:
            #Clear the previous symbols:
            client({"which_array":"live_candidates","action":"clear","item":""})
            for symbol in updated_symbols:
                if "PAX" in symbol or "USD" in symbol or "USDT" in symbol:
                    # print(symbol)
                    updated_symbols.remove(symbol)
                else:
                    client({"which_array":"live_candidates","action":"append","item":symbol})
        except Exception as e:
            print(e)
        print(updated_symbols)
        #Sleep for x hours until next update
        for _ in range(4): #How many hours the function will wait
            for _ in range(60):
                time.sleep(60)



if __name__ == "__main__":
    update_candidates()
    # print(client({"which_array":"live_candidates","action":"read","item":""}))





        