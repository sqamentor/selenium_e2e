#📁 Step 3.1: Install ffmpeg
#Make sure ffmpeg is installed and added to PATH:
#Windows: https://ffmpeg.org/download.html
#-------------------------------------------------------------------
import subprocess
import os
import time
import pytest

@pytest.fixture(scope="function")
def record_video(request):
    record_enabled = os.getenv("RECORD_VIDEO", "false").lower() == "true"
    video_name = f"recordings/{request.node.name}.mp4"

    if not record_enabled:
        yield None
        return

    os.makedirs("recordings", exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-video_size", "1366x768",
        "-f", "gdigrab",
        "-i", "desktop",
        "-framerate", "15",
        video_name
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    yield video_name
    proc.terminate()
    time.sleep(1)