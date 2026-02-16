from collections import Counter

def calculate_gc_content(seq: str) -> float:
    seq = seq.upper()
    counts = Counter(seq)

    a = counts.get("A", 0)
    t = counts.get("T", 0)
    g = counts.get("G", 0)
    c = counts.get("C", 0)

    total = a + t + g + c
    if total == 0:
        return 0

    return (g + c) / total
