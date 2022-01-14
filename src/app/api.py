import log
import tinyweb
import settings

from . import radiator

app = tinyweb.webserver(debug=True)


@app.catchall()
async def catchall(req, resp):
    resp.code = 404
    await resp.start_html()
    await resp.send("No such resource")


def add_endpoint(base, endpoints):
    for url, cls in endpoints.items():
        app.add_resource(cls, f"{base}/{url}")


app.add_resource(log.api, "/api/syslog")
add_endpoint("/api/radiator", radiator.api)
add_endpoint("/api", settings.api)

MIMETYPES = {"json": "application/json"}


@app.route("/static/<fn>")
async def static(req, resp, fn):
    if ".." in fn:
        await resp.start_html()
        await resp.send("Hahaha, very funny.")
    else:
        suffix = fn.split(".")[-1]
        content_type = MIMETYPES.get(suffix, "text/plain")
        await resp.send_file(f"static/{fn}", content_type=content_type)


app.run(port=80, loop_forever=False, host="0.0.0.0")
