"""
Helper to emit and keep track of errors.
"""

NUM_ERRORS = 0

def err(loc, *args, **kwargs):
    global NUM_ERRORS
    NUM_ERRORS += 1
    print(f"{loc}: error: "+" ".join(map(str, args)), **kwargs)

def note(loc, *args, **kwargs):
    print(f"{loc}: note: "+" ".join(map(str, args)), **kwargs)
