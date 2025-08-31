from fastapi import Response
from functools import wraps
import inspect

from api.models.base_model import BaseResponse

def rsp_handler(func):
    is_async = inspect.iscoroutinefunction(func)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return BaseResponse(code=500, message='error', data=str(e))
        return BaseResponse(code=200, message='success', data=result)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            return BaseResponse(code=500, message='error', data=str(e))
        return BaseResponse(code=200, message='success', data=result)

    return async_wrapper if is_async else sync_wrapper