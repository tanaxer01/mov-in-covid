from requests import get
import pandas as pd
import os 

def get_file(name, url, where="./datos/", force=False):
    if not os.path.exists(where):
        print(f"[+] created {where}")
        os.mkdir(where)

    if not os.path.exists(where + name + ".csv") or force:
        with open(where + name + ".csv", "w") as archivo:
            print(f"[+] downloaded {where+name}")
            req = get(url).content
            archivo.write( req.decode() )


