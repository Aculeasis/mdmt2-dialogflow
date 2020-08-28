import os
import queue
import threading
import uuid

import dialogflow_v2 as dialogflow

import logger
from languages import LANG_CODE

NAME = 'dialogflow'
API = 665
TERMINAL_VER_MIN = (0, 15, 30)


class Main(threading.Thread):
    CREDENTIALS = 'dialogflow-credentials.json'
    QRY = 'qry'
    CMD = 'cmd'
    MAX_ERRORS = 20

    def __init__(self, cfg, log, owner):
        self.cfg, self.log, self.own = cfg, log, owner
        self.disable = True
        self._err_count = 0
        self._queue = queue.Queue()

        file = os.path.join(self.cfg.path['data'], self.CREDENTIALS)
        if not os.path.isfile(file):
            msg = 'File {} missing in {}. Plugin won\'t work'.format(self.CREDENTIALS, self.cfg.path['data'])
            self.log(msg, logger.CRIT)
            return
        project_id = (self.cfg.load_dict(os.path.splitext(file)[0]) or {}).get('project_id')
        if not project_id:
            self.log('project_id missing in {}'.format(file), logger.CRIT)
            return
        try:
            self._client = dialogflow.SessionsClient.from_service_account_file(file)
            self._session = self._client.session_path(project_id, str(uuid.uuid4()))
        except Exception as e:
            self.log('Session init error: {}'.format(e), logger.CRIT)
            return
        self.disable = False
        super().__init__()

    def start(self):
        self.own.subscribe(self.CMD, self._cmd_callback)
        super().start()

    def join(self, timeout=10):
        if not self.disable:
            self.disable = True
            self.own.unsubscribe(self.CMD, self._cmd_callback)
            self._queue.put_nowait((None, None))
            super().join(timeout)

    def _cmd_callback(self, *_, **kwargs):
        msg = kwargs.get(self.QRY)
        if msg:
            self._queue.put_nowait((self.QRY, msg))

    def run(self):
        while self._err_count < self.MAX_ERRORS:
            cmd, data = self._queue.get()
            if cmd is None:
                break
            elif cmd == self.QRY:
                self._processing(data)

    def _processing(self, text: str):
        try:
            text_input = dialogflow.types.TextInput(text=text, language_code=LANG_CODE.get('IETF', 'en-US'))
            query_input = dialogflow.types.QueryInput(text=text_input)
            response = self._client.detect_intent(self._session, query_input)
        except Exception as e:
            self._err_count += 1
            self.log('Processing error: {}'.format(e), logger.ERROR)
            if self._err_count >= self.MAX_ERRORS:
                self.log('Detected many errors [{}]. Bye!', logger.CRIT)
            return
        else:
            self._err_count = 0

        try:
            result = response.query_result.fulfillment_text
        except AttributeError:
            result = ''
        if result:
            self.own.terminal_call('tts', result)
