from .start import router as start_router
from .masters import router as masters_router
from .prices import router as prices_router

all_routers = (start_router, masters_router, prices_router)
