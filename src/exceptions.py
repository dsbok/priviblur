import asyncio
import traceback
import sanic
import sanic.exceptions

# ponytail: consolidated single-file exceptions module -> multi-file exception directory
class TumblrInvalidRedirect(Exception):
    pass


class ErrorHandlerGroup:
    def __init__(self) -> None:
        self.registered_handlers = {}

    def register(self, *attached_exceptions):
        def registrator(target_handler):
            self.registered_handlers[target_handler] = attached_exceptions
        return registrator

    def register_handlers_into_app(self, app):
        for handler, exceptions in self.registered_handlers.items():
            for exception in exceptions:
                app.error_handler.add(exception, handler)


def create_user_friendly_error_message(request, exception):
    exception_class = exception.__class__
    exception_name = exception_class.__qualname__
    exception_module = exception_class.__module__

    if exception_module is None or exception_module == str.__class__.__module__:
        processed_exception_name = exception_name
    else:
        processed_exception_name = f"{exception_module}.{exception_name}"

    exception_message = str(exception) or None
    context = []

    if tb := getattr(exception, "__traceback__", None):
        parent_dir = getattr(request.app.ctx, "HYPERBLUR_PARENT_DIR_PATH", "")
        for frame in traceback.extract_tb(tb):
            filename = frame.filename
            if parent_dir and filename.startswith(parent_dir):
                local_path = filename[len(parent_dir) + 1 :]
            else:
                local_path = filename
            occurrence = f'File "{local_path}" line {frame.lineno}: in {frame.name}'
            if frame.line:
                occurrence = f"{occurrence}\n  {frame.line.strip()}"
            context.append(occurrence)

    return processed_exception_name, exception_message, "\n".join(reversed(context))


extractor_errors = ErrorHandlerGroup()
miscellaneous_errors = ErrorHandlerGroup()

# Import extractor exceptions dynamically when registered
def register_extractor_handlers(hyperblur_exceptions):
    @extractor_errors.register(hyperblur_exceptions.TumblrLoginRequiredError)
    async def tumblr_error_login_walled(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": "This blog requires an account to view",
                "error_description": "Try finding reblogs instead!",
            },
            status=403,
        )

    @extractor_errors.register(hyperblur_exceptions.TumblrPasswordRequiredBlogError)
    async def tumblr_password_required_blog(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": "This blog requires a password to access",
                "error_description": "Try finding reblogs instead!",
            },
            status=403,
        )

    @extractor_errors.register(hyperblur_exceptions.TumblrRestrictedTagError)
    async def tumblr_error_restricted_tag(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": "This tag has been restricted on Tumblr",
                "error_description": "Try performing a search instead",
            },
            status=403,
        )

    @extractor_errors.register(hyperblur_exceptions.TumblrBlogNotFoundError)
    async def tumblr_error_unknown_blog(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": "Unable to find the requested blog",
                "error_description": "The blog may have been deleted or just never existed in the first place",
            },
            status=404,
        )

    @extractor_errors.register(hyperblur_exceptions.TumblrNon200NorJSONResponse)
    async def tumblr_error_debug_non_json_response_error(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": f"Non 200 status code. Tumblr returned {exception.status_code}",
                "error_description": "Hyperblur might have been ratelimited by Tumblr. Please try again later.",
            },
            status=500,
        )

    @extractor_errors.register(hyperblur_exceptions.TumblrRatelimitReachedError)
    async def tumblr_error_ratelimit(request, exception):
        return await request.app.ctx.render(
            "misc/msg_error",
            context={
                "app": request.app,
                "exception": exception,
                "error_heading": "Hyperblur has been ratelimited by Tumblr",
                "error_description": "Please try again later",
            },
            status=429,
        )


@miscellaneous_errors.register(asyncio.TimeoutError)
async def request_timeout(request, exception):
    return await request.app.ctx.render(
        "misc/msg_error",
        context={
            "app": request.app,
            "exception": exception,
            "error_heading": "Error: Request to Tumblr timed out",
            "error_description": "Hyperblur was unable to complete the request to Tumblr before timing out",
        },
        status=504,
    )


@miscellaneous_errors.register(sanic.exceptions.NotFound, IsADirectoryError)
async def error_404(request, exception):
    return await request.app.ctx.render(
        "misc/msg_error",
        context={
            "app": request.app,
            "exception": exception,
            "error_heading": "404: Not Found",
            "error_description": f'The requested URL "{request.path}" was not found',
        },
        status=404,
    )


@miscellaneous_errors.register(TumblrInvalidRedirect)
async def invalid_redirect(request, exception):
    return await request.app.ctx.render(
        "misc/msg_error",
        context={
            "app": request.app,
            "exception": exception,
            "error_heading": "Error: Tumblr HTTP 301 redirect points to foreign URL",
        },
        status=502,
    )


@miscellaneous_errors.register(Exception)
async def generic_error(request, exception):
    name, message, context = create_user_friendly_error_message(request, exception)
    return await request.app.ctx.render(
        "misc/generic_error",
        context={
            "app": request.app,
            "exception": exception,
            "exception_name": name,
            "exception_message": message,
            "exception_context": context,
        },
        status=500,
    )


def register(app):
    from src import hyperblur_extractor
    register_extractor_handlers(hyperblur_extractor.exceptions)
    extractor_errors.register_handlers_into_app(app)
    miscellaneous_errors.register_handlers_into_app(app)
