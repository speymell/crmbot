from contextvars import ContextVar

business_id_ctx: ContextVar[int | None] = ContextVar("business_id", default=None)


def set_business_id(business_id: int | None) -> None:
    business_id_ctx.set(business_id)


def get_business_id() -> int | None:
    return business_id_ctx.get()
