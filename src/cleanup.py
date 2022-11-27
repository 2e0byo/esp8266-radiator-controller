import os

PRESERVE = "secrets"
DELETE = ("mpy", "py")


def cleanup():
    paths = "/", "/app/", "/static/"
    for path in paths:
        try:
            for f in os.listdir(path):
                suffix = f.split(".")[-1]
                if suffix in DELETE and not any(x in f for x in PRESERVE):
                    os.remove("/".join((path, f)))
        except OSError:
            pass
    for path in paths:
        try:
            os.rmdir(path)
        except OSError:
            pass
