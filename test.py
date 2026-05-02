import winsound

# To START the alarm (Non-blocking and Looping)
winsound.PlaySound("alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

# To STOP the alarm (When the driver wakes up)
winsound.PlaySound(None, winsound.SND_PURGE)