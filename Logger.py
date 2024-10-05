import datetime


class Logger:
    def __init__(self, log_path="./log.md"):
        self.log_path = log_path
    
    def landmark_log(self):
        with open(self.log_path, "a") as f:
            f.write("\n---\n")

    def save_log(self, entry):
        log_line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :\n"+ \
                    f"```\n{entry}\n```\n\n"
        with open(self.log_path, "a") as f:
            f.write(log_line)
