# TODO: to be open sourced
import pickle
import types

# This a modified version of google's deferred library: google.appengine.ext
# It's modified to return the task so that the tasks can be enqueued all at one

_TASKQUEUE_HEADERS = {'Content-Type': 'application/octet-stream'}


def defer(obj, *args, **kwargs):
    task_payload = serialize(obj, *args, **kwargs)
    return task_payload


def _curry_callable(obj, *args, **kwargs):
    if isinstance(obj, types.MethodType):
        return (invoke_member, (obj.__self__, obj.__func__.__name__) + args, kwargs)
    elif isinstance(obj, types.BuiltinMethodType):
        if not obj.__self__:
            return (obj, args, kwargs)
        else:
            return (invoke_member, (obj.__self__, obj.__name__) + args, kwargs)
    elif isinstance(obj, object) and hasattr(obj, '__call__'):
        return (obj, args, kwargs)
    elif isinstance(
        obj,
        (types.FunctionType, types.BuiltinFunctionType, type, types.UnboundMethodType),
    ):
        return (obj, args, kwargs)
    else:
        raise ValueError('obj must be callable')


def serialize(obj, *args, **kwargs):
    curried = _curry_callable(obj, *args, **kwargs)
    return pickle.dumps(curried)


def invoke_member(obj, membername, *args, **kwargs):
    return getattr(obj, membername)(*args, **kwargs)
