# coding: utf-8
import json
import time
import traceback
from threading import Lock
from functools import partial

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient


def print_log(msg, logger_level='debug', log=None):
    if log:
        logger_method = getattr(log, logger_level)
        if logger_level == 'error':
            logger_method(msg, exc_info=1)
        else:
            logger_method(msg)
    else:
        print('{}: {}'.format(logger_level, msg))
        if logger_level == 'error':
            traceback.print_exc()


class MixHTTPClient(object):

    def __init__(self):
        self.io_loop = IOLoop.current()
        self.http_async_client = AsyncHTTPClient(io_loop=self.io_loop)
        self.timeout = 90
        self.sync_run = False
        self.lock = Lock()

    def sync_http_fetch(self, method, url, data=None, headers=None, log=None):
        func = partial(self.async_http_fetch, method, url, data, headers, log)
        with self.lock:
            result = self.io_loop.run_sync(func)
        return result

    @gen.coroutine
    def async_http_fetch(self, method, url, data=None, headers=None, log=None):
        start_time = time.time()
        response = None
        form_data = data
        headers = headers or {}
        # 当 method 为 GET 时，data 必须为 None
        try:
            if data and not isinstance(data, basestring):
                form_data = json.dumps(data)
            print_log("[send_request] ready to send: {}, {}, {}".format(url, method, headers), log=log)
            response = yield self.http_async_client.fetch(
                url,
                method=method,
                body=form_data,
                headers=headers,
                validate_cert=False,
                connect_timeout=self.timeout,
                request_timeout=self.timeout)
            if 200 <= response.code < 205:
                print_log("Payload accepted", log=log)

            status = response.code
            duration = round((time.time() - start_time) * 1000.0, 4)
            print_log("%s %s %s (%sms)" % (status, method, url, duration), log=log)
        except Exception as e:
            if hasattr(e, 'response') and e.response:
                print_log(
                    "Received status code: {}, {}".format(e.response.code,
                                                        e.response.body),
                    logger_level='warn',
                    log=log)
            msg = "Unable to post payload. {} {} {} {}".format(method, url, headers,
                                                            str(data))
            print_log(msg, logger_level='error', log=log)
            if hasattr(e, 'response') and e.response:
                response = e.response
                response.error_info = e
        raise gen.Return(response)


http_client = MixHTTPClient()


def get(url, data=None, headers={}, log=None):
    return http_client.sync_http_fetch('GET', url, data, headers, log)


def post(url, data=None, headers=None, log=None):
    return http_client.sync_http_fetch('POST', url, data, headers, log)


@gen.coroutine
def async_get(url, data=None, headers={'User-Agent': 'Mozilla/5.0'}, log=None):
    result = yield http_client.async_http_fetch('GET', url, data, headers, log)
    raise gen.Return(result)


@gen.coroutine
def async_post(url, data=None, headers=None, log=None):
    result = yield http_client.async_http_fetch('POST', url, data, headers, log)
    raise gen.Return(result)


if __name__ == '__main__':
    foo = post('http://httpbin.org/post', {'a': 'b'}, {'content-type': 'application/json'})
    print(foo.body)
    too = get('http://httpbin.org/get')
    print(too.body)