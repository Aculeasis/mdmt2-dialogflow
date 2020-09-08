import json


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__ if isinstance(o, BaseWrapper) else super().default(o)


class BaseWrapper:
    def __init__(self, data):
        for key in (x for x in dir(self) if not x.startswith('_') and x != 'pretty'):
            value = getattr(data, key, None)
            if value is None:
                setattr(self, key, None)
                continue
            self._fill(key, getattr(self, key), value)

    def _fill(self, key: str, default, value):
        if isinstance(default, list):
            result = []
            try:
                result = [default[0](x) for x in value] if default else list(value)
            except (TypeError, AttributeError, ValueError) as e:
                print('1 ', e)
                pass
        else:
            result = None if isclass(default) else default
            try:
                result = (default if isclass(default) else type(default))(value)
            except (TypeError, AttributeError, ValueError):
                pass
        setattr(self, key, result)

    def pretty(self) -> str:
        return json.dumps(self, ensure_ascii=False, indent=1, cls=MyEncoder)


class QueryResult(BaseWrapper):
    # https://cloud.google.com/dialogflow/es/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.QueryResult
    def __init__(self, query_result):
        self.query_text = ''
        self.language_code = ''
        self.speech_recognition_confidence = 0.0
        self.action = ''
        self.parameters = dict()
        self.all_required_params_present = False
        self.fulfillment_text = ''
        self.fulfillment_messages = [Message]
        self.webhook_source = ''
        self.webhook_payload = dict()
        self.output_contexts = [Context]
        # self.intent = Intent
        self.intent_detection_confidence = 0.0
        self.diagnostic_info = dict()
        super().__init__(query_result)


class Context(BaseWrapper):
    # https://cloud.google.com/dialogflow/es/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.Context
    def __init__(self, context):
        self.name = ''
        self.lifespan_count = 0
        self.parameters = dict()
        super().__init__(context)


class Message(BaseWrapper):
    # https://cloud.google.com/dialogflow/es/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.Intent.Message
    def __init__(self, messages):
        self.platform = 0
        super().__init__(messages)
        self.type, self.data = None, None
        for key in (x for x in dir(messages) if not x.startswith('_') and x == x.lower()):
            value = getattr(getattr(messages, key), key, None)
            if value:
                self.type = key
                self.data = [x for x in value] if key == 'text' else value
                break


def isclass(obj):
    return isinstance(obj, type)
