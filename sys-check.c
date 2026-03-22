#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    // Standard SUID setup to run as root
    setuid(0);
    setgid(0);

    printf("--- Official System Banner Viewer ---\n");
    printf("Fetching the current MOTD...\n");

    // VULNERABILITY: This calls 'cat' instead of '/bin/cat'
    // The system will look through the user's $PATH to find 'cat'
    system("cat /etc/motd");

    return 0;
}