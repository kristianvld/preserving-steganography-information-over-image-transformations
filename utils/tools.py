def max_zip(*args, default):
    for i in range(max(len(a) for a in args)):
        yield (a[i] if i < len(a) else default for a in args)