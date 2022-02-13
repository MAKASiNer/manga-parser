import os
import datetime


class Logger:
    def __init__(self, folder: str, debug: bool = True) -> None:
        self.debug = debug
        self.stream = None
        if os.path.isdir(folder):
            date = str(datetime.date.today())
            self.stream = open(os.path.join(folder, date + ".log"), 'a')
        else:
            raise FileNotFoundError("Incorrect log folder")

    def log(self, msg, nl=True, timepoint=True):
        time = str(datetime.datetime.now().time())
        return self.stream.write("{} {}{}".format(
            f"[{time}]" if timepoint else '',
            msg,
            '\n' if nl else ''
        ))

    def logging(self, func):
        def wrapper(*args, **kwargs):
            if self.debug:
                self.log('{} FROM {} WITH *{} **{} => '.format(
                    func.__name__,
                    func.__module__,
                    args,
                    kwargs,
                ), nl=False)

            else:
                self.log('{}.{} => '.format(
                    func.__module__,
                    func.__name__,
                ), nl=False)

            res = func(*args, **kwargs)

            if self.debug:
                self.log(str(res))
            else:
                self.log(type(res))
            return res

        return wrapper

    def __del__(self):
        if self.stream is not None:
            self.stream.close()
