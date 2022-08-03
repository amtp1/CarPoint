def paginate(data_list: list, count: int):
    for i in range(0, len(data_list), count):
        yield data_list[i:i + count]