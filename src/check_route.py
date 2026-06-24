import sys
sys.path.insert(0, ".")
from analyze import analyze, route

analysis = analyze("写一个hello world")
print("analysis:", repr(analysis)[:100])

r = route(analysis)
print("route:", repr(r))
