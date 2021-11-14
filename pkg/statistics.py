
from math import ceil

def get_max(records: "list[list]", field_index: int):
    if len(records) == 0:
        return None
    max_val = records[0][field_index]
    for record in records:
        if record[field_index] > max_val:
            max_val = record[field_index]
    return max_val

def get_min(records: "list[list]", field_index: int):
    if len(records) == 0:
        return None
    max_val = records[0][field_index]
    for record in records:
        if record[field_index] < max_val:
            max_val = record[field_index]
    return max_val

def get_percentiles(records: "list[list]", field_index: int):
    sorted_values = sorted(record[field_index] for record in records)
    sorted_values.sort()
    last_index = len(sorted_values) - 1
    if last_index == -1:
        last_index = 0
        sorted_values = [None]

    return {
        "min": sorted_values[ceil(0 * last_index)],
        "p10": sorted_values[ceil(0.1 * last_index)],
        "p50": sorted_values[ceil(0.5 * last_index)],
        "p90": sorted_values[ceil(0.9 * last_index)],
        "p99": sorted_values[ceil(0.99 * last_index)],
        "max": sorted_values[ceil(1 * last_index)],
    }

def get_avg(records: "list[list]", field_index: int) -> float:
    return sum(record[field_index] for record in records) / len(records)
     