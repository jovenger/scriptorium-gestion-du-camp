
""








import importlib
import sys

sys.dont_write_bytecode = True


def poser_la_cale() -> None:
    import PySide6
    from PySide6 import QtCore, QtGui, QtNetwork, QtWidgets
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    sys.modules["PyQt6"] = PySide6
    for nom, module in (("QtCore", QtCore), ("QtGui", QtGui), ("QtNetwork", QtNetwork), ("QtWidgets", QtWidgets)):
        sys.modules["PyQt6." + nom] = module


def main() -> int:
    poser_la_cale()
    return importlib.import_module("gestion_du_camp.programme").main()


if __name__ == "__main__":
    sys.exit(main())
