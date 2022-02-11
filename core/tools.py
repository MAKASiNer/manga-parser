import dis
from core.module import *
from core.config import *


def select_module(for_url: str) -> BaseModule:
    for model in MODULES:
        if model.server in for_url:
            return model
    return BaseModule()