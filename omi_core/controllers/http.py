from odoo.http import Response, WebRequest
from odoo.service import model as service_model

import logging
_logger = logging.getLogger(__name__)


def _call_function(self, *args, **kwargs):
    """
    Monkey patching method. Odoo 11.0
    Hiện tại request webhook của facebook gửi cả 2 type là 'http' và 'json' nên rơi vào exception BadRequest.
    Phương thức này ghi đè lên method ban đầu.
    TODO: Cần tìm giải pháp tối ưu hơn, ví dụ tạo một server riêng để nhận request rồi, chuyển về 1 type và gửi về odoo
          https://github.com/odoo/odoo/issues/7766#issuecomment-230753503
    """
    request = self

    # Phần loại bỏ:
    # if self.endpoint.routing['type'] != self._request_type:
    #     msg = "%s, %s: Function declared as capable of handling request of type '%s' but called with a request of type '%s'"
    #     params = (self.endpoint.original, self.httprequest.path, self.endpoint.routing['type'], self._request_type)
    #     _logger.info(msg, *params)
    #     raise werkzeug.exceptions.BadRequest(msg % params)

    if self.endpoint_arguments:
        kwargs.update(self.endpoint_arguments)

    # Backward for 7.0
    if self.endpoint.first_arg_is_req:
        args = (request,) + args

    # Correct exception handling and concurency retry
    @service_model.check
    def checked_call(___dbname, *a, **kw):
        # The decorator can call us more than once if there is an database error. In this
        # case, the request cursor is unusable. Rollback transaction to create a new one.
        if self._cr:
            self._cr.rollback()
            self.env.clear()
        result = self.endpoint(*a, **kw)
        if isinstance(result, Response) and result.is_qweb:
            # Early rendering of lazy responses to benefit from @service_model.check protection
            result.flatten()
        return result

    if self.db:
        return checked_call(self.db, *args, **kwargs)
    return self.endpoint(*args, **kwargs)


# Monkey patching
WebRequest._call_function = _call_function
