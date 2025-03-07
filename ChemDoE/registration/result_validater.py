
def validate_results(data: dict) -> list[str]:
    errors = []
    if 'VARIABLE' not in data:
        errors.append(f'VARIABLE must be a key in the result JSON!')
    if 'UNIT' not in data:
        errors.append(f'UNIT must be a key in the result JSON!')
    array_length = None
    for k, val in data.items():
        if not isinstance(val, list):
            errors.append(f'{k} must be an array!')
            continue

        if array_length is None:
            array_length = len(val)
        elif len(val) != array_length:
            errors.append(f'{k} must have {array_length} elements!')

        if k not in ['UNIT', 'VARIABLE']:
            try:
                for i, x in enumerate(val):
                    val[i] = float(x)
            except ValueError:
                errors.append(f'{k} must be an array of numbers!')

    return errors