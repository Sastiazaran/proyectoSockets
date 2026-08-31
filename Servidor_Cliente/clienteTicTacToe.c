#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8080
#define BUF_SIZE 1024

int main(int argc, char const *argv[]) {
    const char *host = argc > 1 ? argv[1] : "127.0.0.1";
    const char *user = argc > 2 ? argv[2] : "demo";
    const char *password = argc > 3 ? argv[3] : "demo123";

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0) {
        fprintf(stderr, "Invalid address: %s\n", host);
        close(sock);
        return EXIT_FAILURE;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("connect");
        close(sock);
        return EXIT_FAILURE;
    }

    char payload[BUF_SIZE];
    int n = snprintf(payload, sizeof(payload), "%s\n%s\n", user, password);
    if (n < 0 || n >= (int)sizeof(payload)) {
        fprintf(stderr, "Credentials too long\n");
        close(sock);
        return EXIT_FAILURE;
    }

    if (send(sock, payload, (size_t)n, 0) < 0) {
        perror("send");
        close(sock);
        return EXIT_FAILURE;
    }

    char buffer[BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));
    ssize_t received = read(sock, buffer, sizeof(buffer) - 1);
    if (received < 0) {
        perror("read");
        close(sock);
        return EXIT_FAILURE;
    }
    buffer[received] = '\0';
    printf("%s\n", buffer);

    close(sock);
    return strstr(buffer, "Auth successful") ? 0 : 1;
}
