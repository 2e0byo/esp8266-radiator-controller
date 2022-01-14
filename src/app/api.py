import log
import tinyweb

from . import radiator

from . import scheduler


app = tinyweb.webserver(debug=True)

app.add_resource(log.api, "/api/syslog/")


@app.resource("/api/radiator/next/")
async def next(data):
    print("in next")
    print(data)
    return {"next-wakeup": radiator.scheduler.next_wakeup}


rules_list = scheduler.RulesListApi(radiator.scheduler)
app.add_resource(rules_list, "/api/radiator/rules/")

app.run(port=80, loop_forever=False, host="0.0.0.0")
