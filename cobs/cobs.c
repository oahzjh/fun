// This source is copy and modified from:
// https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

enum {
  READ_CHUNK = 256,
  LINE_LENGTH = 8,
};

typedef enum {
  PRETTY_PRINT_FORMAT_BYTE = 1,
  PRETTY_PRINT_FORMAT_HALF = 2,
  PRETTY_PRINT_FORMAT_WORD = 4,
} pretty_print_format_t;

#define StartBlock() (code_ptr = dst++, code = 1)
#define FinishBlock() (*code_ptr = code)

/*
 * stuff_data byte stuffs "length" bytes of data
 * at the location pointed to by "ptr", writing
 * the output to the location pointed to by "dst".
 *
 * Returns the length of the encoded data.
 */
size_t stuff_data(const uint8_t *ptr, size_t length, uint8_t *dst) {
  const uint8_t *start = dst, *end = ptr + length;
  uint8_t code, *code_ptr; /* Where to insert the leading count */

  StartBlock();
  while (ptr < end) {
    if (code != 0xFF) {
      uint8_t c = *ptr++;
      if (c != 0) {
        *dst++ = c;
        code++;
        continue;
      }
    }
    FinishBlock();
    StartBlock();
  }
  FinishBlock();
  return dst - start;
}

/*
 * unstuff_data decodes "length" bytes of data at
 * the location pointed to by "ptr", writing the
 * output to the location pointed to by "dst".
 *
 * Returns the length of the decoded data
 * (which is guaranteed to be <= length).
 */
size_t unstuff_data(const uint8_t *ptr, size_t length, uint8_t *dst) {
  const uint8_t *start = dst, *end = ptr + length;
  uint8_t code = 0xFF, copy = 0;

  for (; ptr < end; copy--) {
    if (copy != 0) {
      *dst++ = *ptr++;
    } else {
      if (code != 0xFF)
        *dst++ = 0;
      copy = code = *ptr++;
      if (code == 0)
        break; /* Source length too long */
    }
  }
  return dst - start;
}

void pretty_print(unsigned char *ptr, ssize_t length,
                  pretty_print_format_t format) {
  int i = 0;
  unsigned int segment_len = format;
  unsigned char *segment_ptr = malloc(segment_len);
  unsigned char *end_ptr = ptr + length;

  while (end_ptr > ptr) {
    if (i % LINE_LENGTH == 0) {
      printf("%04x: ", i * segment_len);
    }

    memcpy(segment_ptr, ptr, segment_len);
    ptr += segment_len;

    // TODO: Consider different endianess
    for (int x = 0; x < segment_len; x++) {
      printf("%02x", segment_ptr[x]);
    }
    printf(" ");

    // Check reached end of line and need to wrap
    if (++i % LINE_LENGTH == 0) {
      printf("\n");
    }
  }

  // Just to be nice. Check if we ended on a new line, if not add a newline
  if (i % LINE_LENGTH != 0) {
    printf("\n");
  }

  fflush(stdout);
  free(segment_ptr);
}

int main(int argc, char *argv[]) {
  for (int i = 1; i < argc; i++) {
    printf("\nfilename: %s\n", argv[i]);
    FILE *fd = fopen(argv[i], "r");
    unsigned char *buffer = malloc(READ_CHUNK);
    size_t buffer_len = fread(buffer, 1, READ_CHUNK, fd);
    if (buffer_len > 0) {
      printf("Original: %d\n", buffer_len);
      pretty_print(buffer, buffer_len, PRETTY_PRINT_FORMAT_BYTE);

      // Stuffing bytes
      unsigned char *stuff_buffer = malloc(buffer_len + 2);
      const size_t stuff_len = stuff_data(buffer, buffer_len, stuff_buffer);
      printf("\nStuffed: %d\n", stuff_len);
      pretty_print(stuff_buffer, stuff_len, PRETTY_PRINT_FORMAT_BYTE);

      // Unstuffing bytes
      unsigned char *unstuff_buffer = malloc(buffer_len + 2);
      const size_t unstuff_len =
          unstuff_data(stuff_buffer, buffer_len + 2, unstuff_buffer) - 1;
      printf("\nUnstuffed: %d\n", unstuff_len);
      pretty_print(unstuff_buffer, unstuff_len, PRETTY_PRINT_FORMAT_BYTE);

      if ((unstuff_len != buffer_len) ||
          memcmp(unstuff_buffer, buffer, buffer_len)) {
        printf("Unstuffed does not match original! %d vs %d\n", buffer_len,
               unstuff_len);
        break;
      }

      free(unstuff_buffer);
      free(stuff_buffer);
    }
    free(buffer);
    fclose(fd);
  }
  return 0;
}
