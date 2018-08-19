import os

def httpslize(s):
    return s.replace("http://", "https://")

def main():
    for l in os.listdir("../words/"):
        if not l.endswith("json"):
            continue
        p = "../words/" + l
        with open(p, "r") as f:
            s = httpslize(f.read())
        with open(p, "w") as f:
            f.write(s)

main()