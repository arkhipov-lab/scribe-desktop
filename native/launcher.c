/*
 * Mach-O launcher for Scribe.app
 * Finder double-click requires a real binary, not a shell script.
 * We fork+exec Python and wait so Launch Services keeps this .app alive.
 *
 * Resolution order for Python:
 *   1) Contents/Resources/python/bin/python3  (self-contained dist)
 *   2) Contents/Resources/venv/bin/python3    (embedded/symlinked venv)
 *   3) path in Contents/Resources/venv_python (local/dev builds)
 */
#include <limits.h>
#include <mach-o/dyld.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void show_alert(const char *message) {
  char escaped[1024];
  size_t j = 0;
  for (size_t i = 0; message[i] != '\0' && j + 2 < sizeof(escaped); i++) {
    char c = message[i];
    if (c == '\\' || c == '"') {
      escaped[j++] = '\\';
    }
    if (c == '\n') {
      continue;
    }
    escaped[j++] = c;
  }
  escaped[j] = '\0';

  char cmd[1400];
  snprintf(
      cmd,
      sizeof(cmd),
      "osascript -e 'display alert \"Scribe\" message \"%s\" as critical' >/dev/null 2>&1",
      escaped);
  system(cmd);
}

static int read_first_line(const char *path, char *out, size_t out_size) {
  FILE *f = fopen(path, "r");
  if (!f) {
    return -1;
  }
  if (!fgets(out, (int)out_size, f)) {
    fclose(f);
    return -1;
  }
  fclose(f);
  out[strcspn(out, "\r\n")] = '\0';
  return 0;
}

static int is_executable(const char *path) {
  return path[0] != '\0' && access(path, X_OK) == 0;
}

int main(int argc, char **argv) {
  (void)argc;
  (void)argv;

  char exe_path[PATH_MAX];
  uint32_t exe_size = sizeof(exe_path);
  if (_NSGetExecutablePath(exe_path, &exe_size) != 0) {
    show_alert("Could not locate the application executable.");
    return 1;
  }

  char resolved[PATH_MAX];
  if (realpath(exe_path, resolved) == NULL) {
    strncpy(resolved, exe_path, sizeof(resolved) - 1);
    resolved[sizeof(resolved) - 1] = '\0';
  }

  /* .../Contents/MacOS/Scribe -> .../Contents */
  char *slash = strrchr(resolved, '/');
  if (slash == NULL) {
    show_alert("Invalid application bundle layout.");
    return 1;
  }
  *slash = '\0';
  slash = strrchr(resolved, '/');
  if (slash == NULL) {
    show_alert("Invalid application bundle layout.");
    return 1;
  }
  *slash = '\0';

  char resources[PATH_MAX];
  char backend[PATH_MAX];
  char bin_dir[PATH_MAX];
  char python[PATH_MAX];
  char path_env[PATH_MAX * 3];
  char candidate[PATH_MAX];

  snprintf(resources, sizeof(resources), "%s/Resources", resolved);
  snprintf(backend, sizeof(backend), "%s/backend", resources);
  snprintf(bin_dir, sizeof(bin_dir), "%s/bin", resources);
  python[0] = '\0';

  snprintf(candidate, sizeof(candidate), "%s/python/bin/python3", resources);
  if (is_executable(candidate)) {
    strncpy(python, candidate, sizeof(python) - 1);
    python[sizeof(python) - 1] = '\0';
  }

  if (!is_executable(python)) {
    snprintf(candidate, sizeof(candidate), "%s/venv/bin/python3", resources);
    if (is_executable(candidate)) {
      strncpy(python, candidate, sizeof(python) - 1);
      python[sizeof(python) - 1] = '\0';
    }
  }

  if (!is_executable(python)) {
    char python_cfg[PATH_MAX];
    snprintf(python_cfg, sizeof(python_cfg), "%s/venv_python", resources);
    if (read_first_line(python_cfg, python, sizeof(python)) != 0 ||
        !is_executable(python)) {
      show_alert(
          "Embedded Python runtime is missing. Rebuild with ./scripts/build-dist.sh "
          "or ./scripts/build.sh.");
      return 1;
    }
  }

  const char *old_path = getenv("PATH");
  snprintf(
      path_env,
      sizeof(path_env),
      "%s:/opt/homebrew/bin:/usr/local/bin:%s",
      bin_dir,
      old_path != NULL ? old_path : "/usr/bin:/bin");
  setenv("PATH", path_env, 1);
  setenv("PYTHONPATH", backend, 1);
  setenv("PYTHONDONTWRITEBYTECODE", "1", 1);
  setenv("SCRIBE_ROOT", resources, 1);

  if (chdir(backend) != 0) {
    show_alert("Could not open application resources.");
    return 1;
  }

  pid_t pid = fork();
  if (pid < 0) {
    show_alert("Could not start the application process.");
    return 1;
  }

  if (pid == 0) {
    char *args[] = {python, "app.py", NULL};
    execv(python, args);
    _exit(127);
  }

  int status = 0;
  if (waitpid(pid, &status, 0) < 0) {
    show_alert("Application process failed.");
    return 1;
  }

  if (WIFEXITED(status)) {
    int code = WEXITSTATUS(status);
    if (code == 127) {
      show_alert("Failed to start the Python process.");
    }
    return code;
  }

  return 1;
}
