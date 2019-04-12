import os
import subprocess
from collections import Counter
from queue import PriorityQueue

# TODO: add Unicode support

class Node:
    def __init__(self, char, frequency=0, left=None, right=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __repr__(self):
        return "Node(%s) with weight[%d]" %(self.char, self.frequency)


def compress(text) -> str:
    ''' returns a compressed version of text using the huffman coding algorithm
        returned string will be in the format of encoded huffman tree (used as
        the key to later decompressing) followed by a 1 byte string representing
        the number of zeros used in padding and finally the padded compressed text'''


    queue = PriorityQueue()
    huffman_table= {}
    compressed = ""


    # step 1 -- calculate frequency/weight of each character
    frequency_table = Counter(text)

    # step 2 -- create node forest
    for char, freq in frequency_table.items():
        queue.put(Node(char,freq))

    # step 3 -- merge nodes to create 1 tree
    while queue.qsize() > 1:
        l, r = queue.get(), queue.get()
        queue.put(Node(None, l.frequency + r.frequency, l, r))

    huffman_tree = queue.get() # root node

    # step 4
    build_huffman_table(huffman_tree, "", huffman_table)

    # step 5 -- actual encoding/compression of text based off code_table
    compressed_text = ""
    for char in text:
        compressed_text += huffman_table[char]

    # step 6 -- compress tree do decode can use as key
    compressed_tree = encode_tree(huffman_tree, "")

    # step 7 -- pad compressed to make sure size is multiple of 8
    num_zeros = 8 - (len(compressed_tree) + len(compressed_text)) % 8
    if num_zeros != 0:
        # pad compressed string with zeros
        compressed_text = num_zeros * "0" + compressed_text
    # save padding size so that in decompress we can remove approp num of zeros
    padding_size = f'{num_zeros:08b}'

    # step 8 -- combine into one compressed string that will be written to file
    compressed = compressed_tree + padding_size + compressed_text

    # convert encoded text to bytearray and write to file 1 byte at a time
    compressed_bytearray = bytearray()
    for i in range(0, len(compressed), 8):
        compressed_bytearray.append(int(compressed[i:i+8], 2))

    return compressed_bytearray


def compress_file(original_file, compressed_file):
    ''' takes a file (ascii only so far) and returns a compressed version of it
        using the huffman coding compression scheme '''

    with open(original_file) as r_file, open(compressed_file, "wb") as w_file:
        text = r_file.read()
        compressed_text = compress(text)

        w_file.write(compressed_bytearray)


def decompress(compressed):
    ''' decompresses the given file using the huffman tree as key. The following
    is the format of compressed :
    compressed = compressed_tree + padding_size(1B) + padding + compressed_text
    '''

    # step 1 -- convert compressed text to list format
    bitstring_array = list(compressed)

    # step 2 -- extract & decode tree leaving only padding_size + compressed_text
    huffman_root = decode_tree(bitstring_array)

    # step 3 -- remove padding
    padding_size = int("".join(bitstring_array[:8]), 2)
    bitstring_array = bitstring_array[8:] # remove encoded padding size
    bitstring_array = bitstring_array[padding_size:] # remove actual padding

    # step 4 -- actually decode compressed text
    decompressed_text = ""
    current_node = huffman_root

    for char in bitstring_array:
        current_node = current_node.left if char == '0' else current_node.right

        if current_node.char is not None:   # leaf
            # print("decompressed_text Char {}".format(current_node.char))
            decompressed_text += current_node.char
            current_node = huffman_root     # prepare to re-traverse tree

    return decompressed_text


def decompress_file(compressed_file, decompressed_file):
    ''' read compressed text from file, decode it and write decompressed version
    to output file '''

    compressed_text = ""

    with open(compressed_file, "rb") as r_file, open(decompressed_file, "w") as w_file:

        byte = r_file.read(1)  # read 1 byte at a time
        while len(byte) > 0:
            compressed_byte = f"{bin(ord(byte))[2:]:0>8}"   # seperate?
            compressed_text += compressed_byte
            byte = r_file.read(1)

        decompressed_text = decompress(compressed_text)
        w_file.write(decompressed_text)


# ========= helper functions =========

def build_huffman_table(node, code, huffman_table):
    ''' recursively builds the huffman code table from the huffman tree and
    saves it into the dictionary huffman table '''

    if node.char is not None:   # leaf
        huffman_table[node.char] = code

    else:
        build_huffman_table(node.left, code + "0", huffman_table)
        build_huffman_table(node.right, code + "1", huffman_table)


def encode_tree(node, compressed_tree):
    """Encode huffman tree to save it in the file"""

    if node.char is not None:   # leaf
        compressed_tree += "1"
        compressed_tree += f"{ord(node.char):08b}"
        # print("encode_tree: Char is {}".format(node.char))

    else:
        compressed_tree += "0"
        compressed_tree = encode_tree(node.left, compressed_tree)
        compressed_tree = encode_tree(node.right, compressed_tree)

    return compressed_tree


def decode_tree(compressed: list):
    """Decoding huffman tree to be able to decode the encoded text"""

    bit = compressed.pop(0)

    if bit == "1":
        char = ""
        for bits in range(8):    # each 8 bits are an encoding of a node's char
            char += compressed.pop(0)

        char = chr(int(char, 2)) # decoded char
        # print("decode_tree: Char is {}".format(char))
        return Node(char)


    return Node(None, left=decode_tree(compressed),
                right=decode_tree(compressed))


def calculate_ratio(original_file, compressed_file):
    bytes_before = os.path.getsize(original_file)
    bytes_after = os.path.getsize(compressed_file)

    compression_percent = round(100 - bytes_after / bytes_before * 100, 1)

    print(f"before: {bytes_before} bytes || after: {bytes_after} bytes || "
          f"compression {compression_percent}%")



if __name__ == "__main__":

    string = 'go go go go gophers gopher gophers'
    compressed = compress(string)
    print(compressed)

    # files = ["sonnets.txt", "as_you_like_it_scene1.txt", "venus_and_adonis.txt"]
    # for file in files:
    #
    #     compressed = "compressed.txt"
    #     decompressed = "decompressed.txt"
    #
    #     compress_file(file, compressed)
    #     calculate_ratio(file, compressed)
    #     decompress_file(compressed, decompressed)
    #
    #
    #     # check that our decompressed file matches the original file
    #     current_dir = os.getcwd()
    #     decompressed =  current_dir + "/test_files/" + decompressed
    #     original = current_dir + "/test_files/" + file
    #
    #     cp = subprocess.run(["diff", original, decompressed])
    #     returncode = cp.returncode
    #
    #     if returncode == 0:     # diff returns 0 if files match
    #         print('YASS! This file was compressed and decompressed correctly.')
    #
    #     else:
    #         print('Error -- somewhere somehow something went wrong.')
