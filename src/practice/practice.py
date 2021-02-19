import os

print("Hello Docker World")
print(os.path.realpath(__file__))
print(os.getenv("INPUT_FILE"))


def practice_pytest(a, b):
    return a + b
