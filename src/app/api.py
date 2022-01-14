import log
import tinyweb

from . import radiator

from . import scheduler


app = tinyweb.webserver(debug=True)

app.add_resource(log.api, "/api/syslog")


@app.resource("/api/radiator/next/")
async def next(data):
    print("in next")
    print(data)
    return {"next-wakeup": radiator.scheduler.next_wakeup}


@app.catchall()
async def catchall(req, resp):
    resp.code = 404
    await resp.start_html()
    await resp.send("No such resource")


rules_list = scheduler.RulesListAPI(radiator.scheduler)
app.add_resource(rules_list, "/api/radiator/rules")

rules = scheduler.RuleAPI(radiator.scheduler)
app.add_resource(rules, "/api/radiator/rules/<rule_id>")


app.run(port=80, loop_forever=False, host="0.0.0.0")
