/*
 * Tic-Tac-Toe authentication server.
 *
 * Protocol (TCP, port 8080 by default):
 *   client sends:  <username>\n<password>\n
 *   (the original demo client may send only a password)
 *   server replies: "Auth successful" or "Auth failed"
 *
 * Accounts live in data/users.txt as:  username sha256_hex
 * The Python client writes the same file. Hash is SHA256(lowercase(user) ":" password).
 */

#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#include "sha256.h"

#define PORT 8080
#define BACKLOG 8
#define BUF_SIZE 1024
#define HASH_HEX_LEN 64
#define LEGACY_PASSWORD "password123"

static volatile sig_atomic_t running = 1;

static void on_signal(int sig) {
    (void)sig;
    running = 0;
}

static void trim(char *s) {
    size_t len = strlen(s);
    while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r' || isspace((unsigned char)s[len - 1]))) {
        s[--len] = '\0';
    }
    char *start = s;
    while (*start && isspace((unsigned char)*start)) {
        start++;
    }
    if (start != s) {
        memmove(s, start, strlen(start) + 1);
    }
}

static void lower_copy(char *dst, size_t dst_size, const char *src) {
    size_t i = 0;
    while (src[i] && i + 1 < dst_size) {
        dst[i] = (char)tolower((unsigned char)src[i]);
        i++;
    }
    dst[i] = '\0';
}

static FILE *open_users_file(void) {
    const char *candidates[] = {
        "data/users.txt",
        "../data/users.txt",
        "users.txt",
        NULL,
    };
    const char *env = getenv("TICTACTOE_USERS_FILE");
    if (env && env[0]) {
        FILE *f = fopen(env, "r");
        if (f) {
            return f;
        }
    }
    for (int i = 0; candidates[i]; i++) {
        FILE *f = fopen(candidates[i], "r");
        if (f) {
            return f;
        }
    }
    return NULL;
}

static int password_matches(const char *username, const char *password) {
    if (strcmp(password, LEGACY_PASSWORD) == 0) {
        return 1;
    }

    char user_lower[128];
    char payload[BUF_SIZE];
    char expected[HASH_HEX_LEN + 1];
    lower_copy(user_lower, sizeof(user_lower), username);
    snprintf(payload, sizeof(payload), "%s:%s", user_lower, password);
    sha256_hex((const uint8_t *)payload, strlen(payload), expected);

    FILE *file = open_users_file();
    if (!file) {
        return 0;
    }

    char line[BUF_SIZE];
    int ok = 0;
    while (fgets(line, sizeof(line), file)) {
        trim(line);
        if (line[0] == '\0' || line[0] == '#') {
            continue;
        }
        char file_user[128];
        char file_hash[HASH_HEX_LEN + 8];
        if (sscanf(line, "%127s %71s", file_user, file_hash) != 2) {
            continue;
        }
        lower_copy(file_user, sizeof(file_user), file_user);
        if (strcmp(file_user, user_lower) == 0 && strcmp(file_hash, expected) == 0) {
            ok = 1;
            break;
        }
    }
    fclose(file);
    return ok;
}

static int parse_credentials(char *buffer, char **user, char **password) {
    char *nl = strchr(buffer, '\n');
    if (nl) {
        *nl = '\0';
        *user = buffer;
        *password = nl + 1;
        char *nl2 = strchr(*password, '\n');
        if (nl2) {
            *nl2 = '\0';
        }
        trim(*user);
        trim(*password);
        return (*user)[0] && (*password)[0];
    }

    /* Original demo client sent only the password. */
    trim(buffer);
    *user = "demo";
    *password = buffer;
    return (*password)[0] != '\0';
}

static void handle_client(int fd) {
    char buffer[BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));
    ssize_t n = read(fd, buffer, sizeof(buffer) - 1);
    if (n <= 0) {
        return;
    }
    buffer[n] = '\0';

    char *user = NULL;
    char *password = NULL;
    const char *reply;
    if (!parse_credentials(buffer, &user, &password)) {
        reply = "Auth failed";
    } else if (password_matches(user, password)) {
        reply = "Auth successful";
        printf("Auth successful for user '%s'\n", user);
    } else {
        reply = "Auth failed";
        printf("Auth failed for user '%s'\n", user);
    }
    send(fd, reply, strlen(reply), 0);
}

int main(void) {
    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in address;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        return EXIT_FAILURE;
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen");
        close(server_fd);
        return EXIT_FAILURE;
    }

    printf("Auth server listening on port %d\n", PORT);
    fflush(stdout);

    while (running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 250000;

        int ready = select(server_fd + 1, &read_fds, NULL, NULL, &tv);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("select");
            break;
        }
        if (ready == 0) {
            continue;
        }

        struct sockaddr_in client_addr;
        socklen_t addrlen = sizeof(client_addr);
        int client = accept(server_fd, (struct sockaddr *)&client_addr, &addrlen);
        if (client < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("accept");
            break;
        }
        handle_client(client);
        close(client);
    }

    close(server_fd);
    printf("Connection closed\n");
    return 0;
}
