
"""
AIRDESK — Hand Gesture PC Control System
Entry point. Run this file to start the application.
"""
from gesture_v3.core.orchestrator import SystemController

if __name__ == "__main__":
    app = SystemController()
    app.run()
