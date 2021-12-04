# All the different evironment variables and user settings will go here and be used by the bot 
#Old key and secret
#API_KEY = ""
#API_SECRET = ""
from console_manager.console_manager import Console


PREFERED_TRADING_ASSET = "ETH" #Main base asset to trade in 
API_KEY = ""
API_SECRET = ""
POSSIBLE_LONG_TRIGGERS = ["volume_spike","price_spike","bollband_stochrsi","ema_crossover"]
POSSIBLE_SELL_TRIGGERS = ["profit_range","stochastic_peak","rsi_peak","top_bb_band_reached"]
#Instance of console_manager.Console(). Object can get imported to other parts of script so that everything gets printed in one window
MAIN_CONSOLE = Console(color="b",title="KronoBot VER 10.0")
MAIN_CONSOLE.terminate()


def write_main_console(text):
    # try:
    MAIN_CONSOLE.write(str(text))
    # except Exception as e:
    #     raise Exception(f"Error with writing to main console: {str(e)}")




















