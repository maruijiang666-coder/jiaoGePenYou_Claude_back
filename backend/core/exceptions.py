from ninja import NinjaAPI


def register_exception_handlers(api: NinjaAPI):
    @api.exception_handler(Exception)
    def global_handler(request, exc):
        return api.create_response(
            request,
            {"success": False, "error": str(exc)},
            status=500,
        )
