#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝

import cv2
import time
import os
import sys
import shutil
import numpy as np

class Player:
    def __init__(self, run_duration=None):
        self.run_duration = run_duration
        self.ascii_chars = np.array(list(
            " .'`^\",:;Il!i~+_-?][}{1)(|\\/"
            "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao"
            "*#MW&8%B@$"
        ))
        self.char_ratio = 0.3

    def frame_to_ascii_color(self, frame):
        term_size = shutil.get_terminal_size()
        canvas_width = term_size.columns
        canvas_height = int(term_size.lines * 0.95)

        h, w, _ = frame.shape
        aspect_ratio = h / w
        new_height = int(aspect_ratio * canvas_width * self.char_ratio)

        if new_height > canvas_height:
            new_height = canvas_height

        resized = cv2.resize(frame, (canvas_width, new_height))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        indices = (gray.astype(np.int32) * (len(self.ascii_chars) - 1) // 255)

        output_lines = []
        for y in range(new_height):
            line = []
            for x in range(canvas_width):
                # Optimization: Access pixel directly
                b, g, r = resized[y, x] 
                char = self.ascii_chars[indices[y, x]]
                line.append(f"\033[38;2;{r};{g};{b}m{char}")
            output_lines.append("".join(line))

        return "\n".join(output_lines) + "\033[0m"

    def play(self, rtsp='', title="RTSP Player", width=800, height=600, mode="origin"):
        if not rtsp:
            print("[ERROR] No RTSP URL provided.") # Add this
            return False

        # Mac-specific optimizations for FFmpeg and TCP transport
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;5000000"
        
        cap = cv2.VideoCapture(rtsp)
        
        # Set buffer size to minimum to prevent lag on high-res streams
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            print(f"[ERROR] Failed to open stream: {rtsp}") # Add this
            return False

        if mode == "origin":
            # WINDOW_GUI_EXPANDED helps macOS window management
            cv2.namedWindow(title, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_EXPANDED)
            cv2.resizeWindow(title, width, height)

        if mode == "ascii":
            print("\033[?25l", end="", flush=True)   
            print("\033[2J", end="", flush=True)     

        start_time = time.time()

        try:
            while True:
                if self.run_duration and (time.time() - start_time >= self.run_duration):
                    break

                ret, frame = cap.read()

                if not ret:
                    # Retry logic
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(rtsp)
                    if not cap.isOpened(): break
                    continue

                if mode == "origin":
                    cv2.imshow(title, frame)
                    # INCREASED waitKey to 30ms. This is CRITICAL for macOS 
                    # to prevent the "Not Responding" status.
                    key = cv2.waitKey(30) & 0xFF
                    if key == ord('q') or cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
                        break

                elif mode == "ascii":
                    ascii_frame = self.frame_to_ascii_color(frame)
                    sys.stdout.write("\033[H" + ascii_frame)
                    sys.stdout.flush()
                    # Small sleep to prevent CPU pegged at 100% in ASCII mode
                    time.sleep(0.03)

        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            # Restore terminal cursor
            if mode == "ascii":
                print("\033[?25h\033[0m")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python play.py <rtsp_url> <title> [origin|ascii]")
        sys.exit(1)

    url = sys.argv[1]
    name = sys.argv[2]
    play_mode = sys.argv[3] if len(sys.argv) > 3 else "origin"

    p = Player()
    p.play(rtsp=url, title=name, mode=play_mode)