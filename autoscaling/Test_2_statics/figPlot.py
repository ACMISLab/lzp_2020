
def min_max_range(x, range_values):
    return [round( ((xx - min(x)) / (1.0*(max(x) - min(x)))) * (range_values[1] - range_values[0]) + range_values[0], 2) for xx in x]
