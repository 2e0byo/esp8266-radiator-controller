import os

PRESERVE = "secrets"
DELETE = ("mpy", "py")


def cleanup():
    paths = "/", "/app/"
    for path in paths:
        for f in os.listdir(path):
            suffix = f.split(".")[-1]
            if suffix in DELETE and not any(x in f for x in PRESERVE):
                os.remove("/".join((path, f)))
    for path in paths:
        try:
            os.rmdir(path)
        except OSError:
            pass
