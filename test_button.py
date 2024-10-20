import grovepi
import time

# ボタンが接続されているデジタルポート番号
BUTTON_PORT = 2  # D2ポート

grovepi.pinMode(BUTTON_PORT, "INPUT")

print("Press the button to see the result. Press Ctrl+C to exit.")

try:
    while True:
        button_state = grovepi.digitalRead(BUTTON_PORT)
        if button_state == 1:
            print("Button is pressed")
        else:
            print("Button is not pressed")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
except IOError:
    print("Error")