lst = ["animesh", "aman", "piyush", "Rahul", "Sumonto"]


def device_available(choice):
    pass


def fetch_lst_of_actions():
    pass


print("LIST OF DEVICES :- ")
choice = input("Type device you want to choose :- ")
available = device_available(choice)
if available:
    choice2 = input("Enter the mode (read/control) :-")
    if choice2 == "control":
        lst = fetch_lst_of_actions()
    else:
        # read
        pass
else:
    print("DEVICE NOT AVAILABLE !! ")
