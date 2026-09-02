#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <mach-o/dyld.h>
#include <string.h>

int main() {
    char path[1024];
    uint32_t size = sizeof(path);
    if (_NSGetExecutablePath(path, &size) == 0) {
        char *last_slash = strrchr(path, '/');
        if (last_slash != NULL) {
            *last_slash = '\0';
        }
        char script_path[1024];
        snprintf(script_path, sizeof(script_path), "%s/../Resources/VideoToolbox.py", path);
        execl("/usr/bin/python3", "python3", script_path, NULL);
    }
    return 1;
}
