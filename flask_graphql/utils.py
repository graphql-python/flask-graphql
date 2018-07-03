from copy import copy


def place_files_in_operations(operations, files_map, files):
    paths_to_key = (
        (value.split('.'), key)
        for key, values in files_map.items()
        for value in values
    )
    output = {}
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
        return merge_dicts(
            operations,
            {key: sub_dict},
        )
    if isinstance(operations, list):
        index = int(path[0])
        sub_item = add_file_to_operations(operations[index], file_obj, path[1:])
        return operations[:index] + [sub_item] + operations[index+1:]
    return TypeError('Operations must be a JSON data structure')


def merge_dicts(*dicts):
    # Necessary for python2 support
    if not dicts:
        return {}
    output = copy(dicts[0])
    for d in dicts[1:]:
        output.update(d)
    return output
