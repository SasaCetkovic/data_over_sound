# this thing is used to encode a file into chunks for a data-over-sound transmitte r
# optionally retrieve specific x-th chunk from a file

from rust_enum import enum, Case
import os  # .path.getsize
from math import ceil

@enum
class Result:
    Ok = Case(value = bytearray)
    Err = Case(value = list[int])  # list of indices that failed

# lets make an optimized version that yields all chunks without specifying indices
def chunk(file, chunk_size, max_payload=140):
    file_size = os.path.getsize(file)
    num_chunks = ceil(file_size / chunk_size)
    # metadata: b'$$$$FILE' header, 4 bytes for file size, rest of the bytes for the file name
    filename = os.path.basename(file)
    filename_bytes = filename.encode("utf-8")
    
    header = b'$$$$FILE' + file_size.to_bytes(4, 'big')
    available_for_filename = max_payload - len(header)
    if available_for_filename < 0:
        raise ValueError(f"Cannot send file, metadata packet is too large for payload size {max_payload}")
    
    if len(filename_bytes) > available_for_filename:
        # truncate filename
        filename_bytes = filename_bytes[:available_for_filename]

    yield header + filename_bytes
    with open(file, 'rb') as f:
        for i, chunk_data in enumerate(iter(lambda: f.read(chunk_size), b'')): # read until EOF
            chunk = i.to_bytes(2, 'big') + num_chunks.to_bytes(2, 'big') + chunk_data
            if len(chunk) > max_payload:
                # This should not happen with correct chunk_size calculation in main.py
                # but as a safeguard:
                raise ValueError(f"Data chunk is too large for payload size {max_payload}")
            yield chunk
    # yield the FEND$$$$ footer to not make the receiver wait 30 seconds for the next chunk
    footer = b'FEND$$$$'
    if len(footer) > max_payload:
        raise ValueError(f"Cannot send file, footer packet is too large for payload size {max_payload}")
    yield footer


def chunk_text(text: str, chunk_size: int, max_payload: int):
    """
    chunks a string into chunks for a data-over-sound transmitter
    """
    text_bytes = text.encode('utf-8')
    text_size = len(text_bytes)
    num_chunks = ceil(text_size / chunk_size)
    
    header = b'$$$$TEXT' + text_size.to_bytes(4, 'big')
    if len(header) > max_payload:
        raise ValueError(f"Cannot send text, metadata packet is too large for payload size {max_payload}")
    yield header

    for i in range(num_chunks):
        chunk_data = text_bytes[i*chunk_size : (i+1)*chunk_size]
        chunk = i.to_bytes(2, 'big') + num_chunks.to_bytes(2, 'big') + chunk_data
        if len(chunk) > max_payload:
            # This should not happen with correct chunk_size calculation in main.py
            # but as a safeguard:
            raise ValueError(f"Data chunk is too large for payload size {max_payload}")
        yield chunk
    
    footer = b'TEND$$$$'
    if len(footer) > max_payload:
        raise ValueError(f"Cannot send text, footer packet is too large for payload size {max_payload}")
    yield footer


def dechunk(chunk_list):
    '''
    dechunks a list of chunks into a file

    args:
        chunk_list: list of chunks, each chunk is a tuple of (chunk_idx, num_chunks, chunk_data)

    returns:
        Result.Ok if successful, Result.Err with a list of indices that failed
    '''
# delete all chunks that are start/end markers for file or text transfers
    chunk_list = [chunk for chunk in chunk_list if not chunk.startswith(b'FEND$$$$') and not chunk.startswith(b'$$$$FILE') and not chunk.startswith(b'TEND$$$$') and not chunk.startswith(b'$$$$TEXT')]
    # sort the chunks by index via the first 2 bytes of the chunk
    if not chunk_list:
        return Result.Err([])
    chunk_list.sort(key=lambda x: int.from_bytes(x[0:2], 'big'))
    num_chunks = int.from_bytes(chunk_list[0][2:4], 'big')
    file = bytearray()
    chunk_idcs = [int.from_bytes(chunk[0:2], 'big') for chunk in chunk_list]
    failed = [i for i in range(num_chunks) if i not in chunk_idcs]
    if failed:
        return Result.Err(failed)
    for i, chunk in enumerate(chunk_list):
        chunk_idx = int.from_bytes(chunk[0:2], 'big')
        # remove the chunk index
        raw_chunk = chunk[4:]
        file.extend(raw_chunk)
    return Result.Ok(file)


#[cfg(test)]  # this is a valid python comment that looks rusty
def test_chunker():
    # test the chunker
    chunk_size = 128
    with open('files/helloworld.txt', 'rb') as f:
        file_data = f.read()
    file = 'files/helloworld.txt'
    chunks = list(chunk(file, chunk_size, max_payload=140))
    print(len(chunks))
    match dechunk(chunks):
        case Result.Ok(data):
            assert data == file_data
        case Result.Err(failed):
            assert False, f"Failed chunks: {failed}"
    
    # test chunk_text
    text = "hello world this is a long text to test chunking"
    chunks = list(chunk_text(text, 10, 14))
    match dechunk(chunks):
        case Result.Ok(data):
            assert data == text.encode('utf-8')
        case Result.Err(failed):
            assert False, f"Failed chunks: {failed}"

    # lets now break the chunks, miss second and fourth chunk
    chunks.pop(4)
    chunks.pop(2)  # what fool was i, before i popped 2 and 4, and the 4th moved to 3rd place!!!
    match dechunk(chunks):
        case Result.Ok(data):
            assert False, "Should have failed"
        case Result.Err(failed):
            print(failed)
            assert failed == [1, 3]


if __name__ == '__main__':
    test_chunker()
    print("All tests passed")
