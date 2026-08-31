#include <stdio.h>
#include <string.h>
#include "../Servidor_Cliente/sha256.h"

int main(int argc, char **argv) {
    const char *input = argc > 1 ? argv[1] : "demo:demo123";
    char out[65];
    sha256_hex((const uint8_t *)input, strlen(input), out);
    printf("%s\n", out);
    return 0;
}
