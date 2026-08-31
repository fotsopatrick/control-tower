def depends(*args):
    def wrapper(f): return f
    return wrapper
def model(f): return f
def model_create_multi(f): return f
