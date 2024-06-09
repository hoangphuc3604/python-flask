def decorator(func):
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper

@decorator
def add(a, b):
    return a+b

add(1, 2)