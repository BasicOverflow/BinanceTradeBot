# https://stackoverflow.com/questions/19479504/how-can-i-open-two-consoles-from-a-single-script
import sys, time, os, locale
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE

class Console(Popen):
    NumConsoles = 0
    def __init__(self, color=None, title=None):
        Console.NumConsoles += 1

        cmd = "import sys, os, locale"
        cmd += "\nos.system(\'color " + color + "\')" if color is not None else ""
        title = title if title is not None else "console #" + str(Console.NumConsoles)
        cmd += "\nos.system(\"title " + title + "\")"
        # poor man's `cat`
        cmd += """
print(sys.stdout.encoding, locale.getpreferredencoding() )
endcoding = locale.getpreferredencoding()
for line in sys.stdin:
    sys.stdout.buffer.write(line.encode(endcoding))
    sys.stdout.flush()
"""
        cmd = sys.executable, "-c", cmd
        # print(cmd, end="", flush=True)
        super().__init__(cmd, stdin=PIPE, bufsize=1, universal_newlines=True, creationflags=CREATE_NEW_CONSOLE, encoding='utf-8')
        #Create some whitespace
        self.write('''
-----------------------------------------------------------------------------------------------------------------------

 /$$   /$$                                         /$$$$$$$              /$$                               
| $$  /$$/                                        | $$__  $$            | $$                               
| $$ /$$/   /$$$$$$   /$$$$$$  /$$$$$$$   /$$$$$$ | $$  \ $$  /$$$$$$  /$$$$$$                             
| $$$$$/   /$$__  $$ /$$__  $$| $$__  $$ /$$__  $$| $$$$$$$  /$$__  $$|_  $$_/                             
| $$  $$  | $$  \__/| $$  \ $$| $$  \ $$| $$  \ $$| $$__  $$| $$  \ $$  | $$                               
| $$\  $$ | $$      | $$  | $$| $$  | $$| $$  | $$| $$  \ $$| $$  | $$  | $$ /$$                           
| $$ \  $$| $$      |  $$$$$$/| $$  | $$|  $$$$$$/| $$$$$$$/|  $$$$$$/  |  $$$$/                           
|__/  \__/|__/       \______/ |__/  |__/ \______/ |_______/  \______/    \___/                             
                                                                                                                                                                                                         
                                                                                                           
 /$$    /$$                              /$$                             /$$    /$$$$$$      /$$$$$$       
| $$   | $$                             |__/                           /$$$$   /$$$_  $$    /$$$_  $$      
| $$   | $$ /$$$$$$   /$$$$$$   /$$$$$$$ /$$  /$$$$$$  /$$$$$$$       |_  $$  | $$$$\ $$   | $$$$\ $$      
|  $$ / $$//$$__  $$ /$$__  $$ /$$_____/| $$ /$$__  $$| $$__  $$        | $$  | $$ $$ $$   | $$ $$ $$      
 \  $$ $$/| $$$$$$$$| $$  \__/|  $$$$$$ | $$| $$  \ $$| $$  \ $$        | $$  | $$\ $$$$   | $$\ $$$$      
  \  $$$/ | $$_____/| $$       \____  $$| $$| $$  | $$| $$  | $$        | $$  | $$ \ $$$   | $$ \ $$$      
   \  $/  |  $$$$$$$| $$       /$$$$$$$/| $$|  $$$$$$/| $$  | $$       /$$$$$$|  $$$$$$//$$|  $$$$$$/      
    \_/    \_______/|__/      |_______/ |__/ \______/ |__/  |__/      |______/ \______/|__/ \______/       

-----------------------------------------------------------------------------------------------------------------------
        ''')


    def write(self, msg):
        self.stdin.write(msg + "\n" )




if __name__ == "__main__":
    myConsole = Console(color="c0", title="test error console")
    myConsole.write("Thank you jfs. Cool explanation")
    time.sleep(5)
