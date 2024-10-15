import datetime


class Logger:
    def __init__(self, is_active = False, log_path="./files/log.md"):
        self.log_path = log_path
        self.is_active = is_active
    
    def landmark_log(self):
        if not self.is_active:
            return
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("\n---\n")

    def save_log(self, entry):
        if not self.is_active:
            return
        
        log_line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :\n"+ \
                    f"```\n{entry}\n```\n\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line)
