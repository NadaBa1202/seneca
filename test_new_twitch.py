import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

from esports_analytics.services.chat.streamlit_twitch import start_twitch_monitoring, stop_twitch_monitoring

def test_callback(message):
    print(f"✅ {message['username']}: {message['message']}")

print("Connecting to a popular channel...")
success = start_twitch_monitoring('shroud', test_callback)
if success:
    print("Connected! Waiting for messages for 15 seconds...")
    time.sleep(15)
    print("Stopping connection...")
else:
    print("Failed to connect")
stop_twitch_monitoring()
print("Test completed!")
