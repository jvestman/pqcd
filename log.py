from collections import defaultdict
import time
from datetime import datetime


class Log:

    def __init__(self, label, channel_bandwidth):
        self.channel_bandwidth = channel_bandwidth
        self.label = label
        self.channel_logs = defaultdict(lambda: "")
        self.channel_last_log = {}
        self.frequency = 0
        self.log_timeout = 30
        self.file = open("log.txt", "a")  # append mode

    def character(self, y, character):
        now = time.time()
        freq = int(self.frequency + y*self.channel_bandwidth)

        # Don't add more than one consequtive space to channel log
        if self.channel_logs[freq][-1:] == " " and character == " ":
            return

        self.channel_logs[freq] += character
        self.channel_last_log[freq] = now
        text = ""

        time_str = datetime.now().strftime("%H:%M:%S")
        for f in sorted(self.channel_logs):
            # Clear channel logs that are older than log_timeout
            if self.channel_last_log[f] + self.log_timeout < now:
                channel_log = self.channel_logs[f].strip()
                if channel_log != "" and len(channel_log) > 5:
                    log_line = time_str + " " + str(f) + " " + channel_log + "\n"
                    self.file.write(log_line)
                self.channel_logs[f] = ""
                self.file.flush()

            # Show last 60 characters of channel log in log frame
            if self.channel_logs[f].strip() != "":
                text += str(f) + "Hz: " + self.channel_logs[f][-60:] + "\n"

        self.label.setText(text)

    def dat(self, y, width):
        pass

    def dit(self, y, width):
        pass

    def unrecognized(self, y, width):
        pass
