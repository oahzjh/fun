""" 
This is a python implementaiton of COBS from:
https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing
"""
import binascii

import os
import sys


def encode(data):
    if len(data) > 254:
        raise ValueError("Data to encode is too long!")

    encode_data = bytearray()
    while data:
        z = data.find(0x00)
        if z == -1:
            break
        encode_data.append(z + 1)
        encode_data += data[0:z]
        data = data[z + 1:]

    if data:
        encode_data.append(len(data) + 1)
        encode_data += data
    else:
        # data ended with zero byte
        encode_data.append(1)

    return encode_data


def decode(data):

    decoded_data = bytearray()
    while data:
        z = data[0]
        if z > len(data):
            break
        decoded_data += data[1:z]
        decoded_data.append(0x00)
        data = data[z:]

    # Remove the last zero
    decoded_data = decoded_data[:-1]

    return decoded_data


def main(argv):
    for fname in argv[1:]:
        data = open(fname, mode='rb').read()
        print("\nOriginal: {}".format(len(data)))
        print(binascii.hexlify(data))

        encoded_data = encode(data)
        print("\nEncoded: {}".format(len(encoded_data)))
        print(binascii.hexlify(encoded_data))

        decoded_data = decode(encoded_data)
        print("\nDecoded: {}".format(len(decoded_data)))
        print(binascii.hexlify(decoded_data))

        if decoded_data != data:
            raise ValueError("Decoded data does not match original!!")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
