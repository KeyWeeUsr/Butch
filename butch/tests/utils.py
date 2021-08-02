class FuncCalls:
    def __init__(self, *calls):
        self.calls = iter(calls)

    def __call__(self, *args, **kwargs):
        return next(self.calls)(*args, **kwargs)
