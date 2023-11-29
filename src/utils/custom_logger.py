import logging
import secrets
from flask import session

def _get_session_id():
    session_key = "session_id"
    if not session.get(session_key):
        session[session_key] = secrets.token_urlsafe(16)
    return session.get(session_key)


def _record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    try:
        record.session_id = _get_session_id()
    except RuntimeError:
        record.session_id = "NO_ACTIVE_SESSION"
    return record


logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s %(session_id)s %(levelname)s %(module)s - %(funcName)s: %(message)s', # figure out why session_id is not working
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

old_factory = logging.getLogRecordFactory()
logging.setLogRecordFactory(_record_factory)

logging.getLogger('werkzeug').setLevel(logging.ERROR)
