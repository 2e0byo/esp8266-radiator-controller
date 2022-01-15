from api_utils import convert_vals


class API:
    def __init__(self, scheduler):
        self._scheduler = scheduler


class RulesListAPI(API):
    def get(self, data):
        yield "["

        started = False
        for rule in self._scheduler.rules:
            if started:
                yield ","
            yield rule.to_json()
            started = True

        yield "]"

    def post(self, data):
        if not "duration" in data:
            raise ValueError("No Duration")

        timespec = list(DateTimeMatch._UNITS.keys())
        if not any(x in data for x in timespec):
            raise ValueError(f"No TimeSpec, should be one or more of {timespec}")

        rule = DateTimeMatch(**{k: convert_vals(v) for k, v in data.items()})
        self._scheduler.append(rule)

        return {"id": rule.id}, 201


class RuleAPI(API):
    def get(self, data, rule_id):
        rule_id = convert_vals(rule_id)

        try:
            rule = next(x for x in self._scheduler.rules if x.id == rule_id)
        except StopIteration:
            return {"error": f"no such rule {rule_id}"}, 404
        return rule.to_json()

    def delete(self, data, rule_id):
        rule_id = convert_vals(rule_id)
        self._scheduler.remove_by_id(rule_id)

        return {"message": "success"}


class StateAPI(API):
    def get(self, data):
        return dict(state=self._scheduler.state)


class NextAPI(API):
    def get(self, data):
        return self._scheduler.next_wakeup.to_json()


class OnceoffAPI(API):
    def post(self, data):
        try:
            duration = convert_vals(data["duration"])
            self._scheduler.append_once(duration)
            return {"message": "success"}
        except Exception as e:
            return {"error": str(e)}, 400

    def delete(self, data):
        try:
            self._scheduler.pop_once()
            return {"message": "success"}
        except Exception as e:
            return {"error": str(e)}, 400


class JustifyAPI(API):
    def get(self, data):
        return self._scheduler.justify()
