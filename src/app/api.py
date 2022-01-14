import log
import tinyweb

app = tinyweb.webserver()

app.add_resource(log.api, "/api/syslog/")


app.run(port=80, loop_forever=False, host="0.0.0.0")
