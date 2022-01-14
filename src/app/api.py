import log
import tinyweb

from . import radiator

app = tinyweb.webserver(debug=True)


@app.catchall()
async def catchall(req, resp):
    resp.code = 404
    await resp.start_html()
    await resp.send("No such resource")


app.add_resource(log.api, "/api/syslog")
for url, cls in radiator.api.items():
    app.add_resource(cls, f"/api/radiator/{url}")

app.run(port=80, loop_forever=False, host="0.0.0.0")
