def place_files_in_operations(operations, files_map, files):
    paths_to_key = (
        (value.split('.'), key)
        for key, values in files_map.items()
        for value in values
    )
    output = new_merged_dict(operations)
    output.update(operations)
    for path, key in paths_to_key:
        file_obj = files[key]
        output = add_file_to_operations(output, file_obj, path)
    return output


def add_file_to_operations(operations, file_obj, path):
    if not path:
        return file_obj
    if isinstance(operations, dict):
        key = path[0]
        sub_dict = add_file_to_operations(operations[key], file_obj, path[1:])
        return new_merged_dict(operations, {key: sub_dict})
    if isinstance(operations, list):
        index = int(path[0])
        sub_item = add_file_to_operations(operations[index], file_obj, path[1:])
        return new_list_with_replaced_item(operations, index, sub_item)
    return TypeError('Operations must be a JSON data structure')


def new_merged_dict(*dicts):
    # Necessary for python2 support
    output = {}
    for d in dicts:
        output.update(d)
    return output


def new_list_with_replaced_item(input_list, index, new_value):
    # Necessary for python2 support
    output = [i for i in input_list]
    output[index] = new_value
    return output
