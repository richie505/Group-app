// "APPSC Lectures.exe": opens app\index.html (next to this exe) in its own window, using the Microsoft Edge that
// Windows 10 and 11 ship with (or Chrome), with its own profile so the reader's progress is kept apart from their
// browser. If neither is found the page opens in the default browser.
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <wchar.h>

static int exists(const wchar_t *p) { DWORD a = GetFileAttributesW(p); return a != INVALID_FILE_ATTRIBUTES && !(a & FILE_ATTRIBUTE_DIRECTORY); }

// "App Paths" registry entry of a browser, e.g. msedge.exe
static int app_path(HKEY root, const wchar_t *exe, wchar_t *out, DWORD cch) {
  wchar_t key[300]; DWORD n = cch * sizeof(wchar_t), type = 0;
  swprintf(key, 300, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\%ls", exe);
  if (RegGetValueW(root, key, NULL, RRF_RT_REG_SZ, &type, out, &n) != ERROR_SUCCESS) return 0;
  return exists(out);
}

static int env_path(const wchar_t *var, const wchar_t *tail, wchar_t *out, DWORD cch) {
  wchar_t base[MAX_PATH];
  DWORD n = GetEnvironmentVariableW(var, base, MAX_PATH);
  if (!n || n >= MAX_PATH) return 0;
  swprintf(out, cch, L"%ls%ls", base, tail);
  return exists(out);
}

static int find_browser(wchar_t *out, DWORD cch) {
  if (app_path(HKEY_LOCAL_MACHINE, L"msedge.exe", out, cch) || app_path(HKEY_CURRENT_USER, L"msedge.exe", out, cch)) return 1;
  if (env_path(L"ProgramFiles(x86)", L"\\Microsoft\\Edge\\Application\\msedge.exe", out, cch)) return 1;
  if (env_path(L"ProgramFiles", L"\\Microsoft\\Edge\\Application\\msedge.exe", out, cch)) return 1;
  if (app_path(HKEY_LOCAL_MACHINE, L"chrome.exe", out, cch) || app_path(HKEY_CURRENT_USER, L"chrome.exe", out, cch)) return 1;
  if (env_path(L"ProgramFiles", L"\\Google\\Chrome\\Application\\chrome.exe", out, cch)) return 1;
  if (env_path(L"ProgramFiles(x86)", L"\\Google\\Chrome\\Application\\chrome.exe", out, cch)) return 1;
  if (env_path(L"LOCALAPPDATA", L"\\Google\\Chrome\\Application\\chrome.exe", out, cch)) return 1;
  return 0;
}

// C:\a b\index.html -> file:///C:/a%20b/index.html (UTF-8, percent-encoded)
static void file_url(const wchar_t *path, wchar_t *out, size_t cch) {
  char u8[4 * MAX_PATH]; size_t o = 0;
  int n = WideCharToMultiByte(CP_UTF8, 0, path, -1, u8, sizeof u8, NULL, NULL);
  o += swprintf(out + o, cch - o, L"file:///");
  for (int i = 0; i < n - 1 && o + 4 < cch; i++) {
    unsigned char c = (unsigned char)u8[i];
    if (c == '\\') out[o++] = L'/';
    else if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '/' || c == ':' || c == '.' || c == '-' || c == '_' || c == '~') out[o++] = (wchar_t)c;
    else o += swprintf(out + o, cch - o, L"%%%02X", c);
  }
  out[o] = 0;
}

int WINAPI wWinMain(HINSTANCE h, HINSTANCE p, PWSTR cmd, int show) {
  (void)h; (void)p; (void)cmd; (void)show;
  wchar_t dir[MAX_PATH], page[MAX_PATH + 32], url[4 * MAX_PATH + 16], browser[MAX_PATH], profile[MAX_PATH], args[8 * MAX_PATH];
  DWORD n = GetModuleFileNameW(NULL, dir, MAX_PATH);
  if (!n || n >= MAX_PATH) return 1;
  wchar_t *slash = wcsrchr(dir, L'\\'); if (slash) *slash = 0;
  swprintf(page, MAX_PATH + 32, L"%ls\\app\\index.html", dir);
  if (!exists(page)) {
    MessageBoxW(NULL, L"The lectures are missing (app\\index.html).\nPlease install APPSC Lectures again.", L"APPSC Lectures", MB_ICONERROR);
    return 1;
  }
  file_url(page, url, 4 * MAX_PATH + 16);
  if (find_browser(browser, MAX_PATH)) {
    wchar_t local[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, 0, local))) swprintf(profile, MAX_PATH, L"%ls\\APPSC Lectures\\profile", local);
    else swprintf(profile, MAX_PATH, L"%ls\\profile", dir);
    swprintf(args, 8 * MAX_PATH,
             L"\"%ls\" --app=\"%ls\" --user-data-dir=\"%ls\" --no-first-run --no-default-browser-check --disable-sync "
             L"--disable-features=Translate,msEdgeSidebarV2 --window-size=1366,860",
             browser, url, profile);
    STARTUPINFOW si; PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof si); si.cb = sizeof si; ZeroMemory(&pi, sizeof pi);
    if (CreateProcessW(browser, args, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
      CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
      return 0;
    }
  }
  // no Edge or Chrome: the default browser shows the same page in a tab
  return (INT_PTR)ShellExecuteW(NULL, L"open", page, NULL, NULL, SW_SHOWNORMAL) > 32 ? 0 : 1;
}
