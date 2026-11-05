
""










from __future__ import annotations

import sys


def au_premier_plan(fenetre) -> bool:
    ""
    try:
        from PyQt6.QtCore import Qt
        if fenetre.isMinimized():
            fenetre.showNormal()
        fenetre.show()
        fenetre.raise_()
        fenetre.activateWindow()

        fenetre.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        fenetre.show()
        fenetre.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        fenetre.show()
    except Exception:
        return False
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
        hwnd = int(fenetre.winId())
        devant = u32.GetForegroundWindow()
        fil_devant = u32.GetWindowThreadProcessId(devant, None)
        mon_fil = k32.GetCurrentThreadId()
        attache = fil_devant != mon_fil and u32.AttachThreadInput(fil_devant, mon_fil, True)
        try:
            u32.ShowWindow(hwnd, 9)
            u32.BringWindowToTop(hwnd)
            u32.SetForegroundWindow(hwnd)
            u32.SetFocus(hwnd)
        finally:
            if attache:
                u32.AttachThreadInput(fil_devant, mon_fil, False)




        if u32.GetForegroundWindow() != hwnd:
            u32.SwitchToThisWindow(hwnd, True)
        if u32.GetForegroundWindow() != hwnd:
            u32.keybd_event(0x12, 0, 0, 0)
            u32.SetForegroundWindow(hwnd)
            u32.keybd_event(0x12, 0, 2, 0)
        return u32.GetForegroundWindow() == hwnd
    except Exception:
        return False


def rendre_au_jeu() -> bool:
    ""

    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        trouvee = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def chaque(hwnd, _):
            if u32.IsWindowVisible(hwnd):
                n = u32.GetWindowTextLengthW(hwnd)
                if n > 0:
                    b = ctypes.create_unicode_buffer(n + 1)
                    u32.GetWindowTextW(hwnd, b, n + 1)
                    if "Kingdom Come" in b.value:
                        trouvee.append(hwnd)
                        return False
            return True

        u32.EnumWindows(chaque, 0)
        if not trouvee:
            return False
        hwnd = trouvee[0]
        u32.SetForegroundWindow(hwnd)
        if u32.GetForegroundWindow() != hwnd:
            u32.SwitchToThisWindow(hwnd, True)
        return u32.GetForegroundWindow() == hwnd
    except Exception:
        return False


def _fenetre_du_jeu():
    ""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        trouvee = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def chaque(hwnd, _):
            if u32.IsWindowVisible(hwnd):
                n = u32.GetWindowTextLengthW(hwnd)
                if n > 0:
                    b = ctypes.create_unicode_buffer(n + 1)
                    u32.GetWindowTextW(hwnd, b, n + 1)
                    if "Kingdom Come" in b.value:
                        trouvee.append(hwnd)
                        return False
            return True

        u32.EnumWindows(chaque, 0)
        return trouvee[0] if trouvee else None
    except Exception:
        return None


def sur_l_ecran_du_jeu(fenetre) -> bool:
    ""

    jeu = _fenetre_du_jeu()
    if jeu is None:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32

        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD)]

        ecran = u32.MonitorFromWindow(jeu, 2)
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        if not u32.GetMonitorInfoW(ecran, ctypes.byref(mi)):
            return False
        w = mi.rcWork
        hwnd = int(fenetre.winId())
        r = wintypes.RECT()
        u32.GetWindowRect(hwnd, ctypes.byref(r))
        larg = min(r.right - r.left, (w.right - w.left) - 40)
        haut = min(r.bottom - r.top, (w.bottom - w.top) - 40)
        x = w.left + ((w.right - w.left) - larg) // 2
        y = w.top + ((w.bottom - w.top) - haut) // 2
        u32.SetWindowPos(hwnd, 0, x, y, larg, haut, 0x0014)
        return True
    except Exception:
        return False
