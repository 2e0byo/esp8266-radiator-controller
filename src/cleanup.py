import os

PRESERVE = "secrets"
DELETE = ("mpy", "py")


def cleanup():
    paths = "/", "/app/"
    for path in paths:
        for f in os.listdir(path):
            suffix = f.split(".")[-1]
            if suffix in DELETE and not PRESERVE in f:
                os.remove("/".join((path, f)))
    os.remove("app")
