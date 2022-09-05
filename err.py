num_errors = 0

def err(loc, *args, **kwargs):
    global num_errors
    num_errors += 1
    print(f"{loc}: error: "+" ".join(map(str, args)), **kwargs)
