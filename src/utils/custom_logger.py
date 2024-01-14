import logging
import secrets
import time
from functools import wraps
from flask import session

# def _get_session_id():
#     session_key = "session_id"
#     if not session.get(session_key):
#         session[session_key] = secrets.token_urlsafe(16)
#     return session.get(session_key)


# def _record_factory(*args, **kwargs):
#     record = old_factory(*args, **kwargs)
#     try:
#         record.session_id = _get_session_id()
#     except RuntimeError:
#         record.session_id = "NO_ACTIVE_SESSION"
#     return record


logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s %(session_id)s %(levelname)s %(module)s - %(funcName)s: %(message)s', # figure out why session_id is not working
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

#old_factory = logging.getLogRecordFactory()
# logging.setLogRecordFactory(_record_factory)

logging.getLogger('werkzeug').setLevel(logging.ERROR)


def time_this_func(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info(f'Function {func.__name__} took {total_time:.2f} seconds')
        return result

    return timeit_wrapper
