import winsound
import sys

# winsound.PlaySound('filename', flag)
winsound.PlaySound("Warn_01.wav", winsound.SND_FILENAME)

# Get the input from the scanner
while True:
    print("Enter a name.  Ctl-c to end.")
    try:
        name = input()
        print(f"You entered the name {name}")
    except:
        print("Ending program")
        sys.exit(0)
