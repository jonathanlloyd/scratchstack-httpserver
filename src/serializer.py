def serialize_response(response):
    if response.status_code < 0:
        raise ValueError('Status code cannot be negative')
    if response.status_code > 999:
        raise ValueError('Status code must be < 1000')

    status_code_string = f"{response.status_code:03d}"
    status_line = f"HTTP/1.1 {status_code_string} {response.reason_phrase}"

    headers_string = ''
    for field_name, field_value in response.headers.items():
        headers_string += f"{field_name}: {field_value}\r\n"

    response_string = f"{status_line}\r\n{headers_string}\r\n{response.body}"
    response_bytes = response_string.encode('utf-8')

    return response_bytes
