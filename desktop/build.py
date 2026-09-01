"""
Скрипт сборки .exe файла для Windows

Собирает только desktop-клиент PyQt6.
Не включает .env, API-ключ, backend и папку data.
"""
import sys
import subprocess
import shutil
from pathlib import Path


APP_NAME = "competition_monitor"
SPEC_FILE = "CompetitorMonitor.spec"


def build_exe():
    """Собрать .exe файл"""
    print("=" * 60)
    print("🔨 СБОРКА DESKTOP ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    current_dir = Path(__file__).parent
    spec_path = current_dir / SPEC_FILE
    
    print("\n📦 Проверка PyInstaller...")
    try:
        import PyInstaller
        print(f"   ✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("   ✗ PyInstaller не установлен")
        print("   Установка из папки desktop: pip install -r requirements.txt")
        sys.exit(1)
    
    if not spec_path.exists():
        print(f"   ✗ Не найден spec-файл: {SPEC_FILE}")
        sys.exit(1)
    
    print("\n🔒 В exe НЕ входят:")
    print("   - .env и PROXY_API_KEY")
    print("   - backend/")
    print("   - data/")
    
    pyinstaller_args = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        SPEC_FILE,
    ]
    
    print(f"\n🚀 Запуск сборки: {APP_NAME}.exe")
    print(f"   Spec: {SPEC_FILE}")
    print("-" * 60)
    
    result = subprocess.run(pyinstaller_args, cwd=current_dir)
    
    if result.returncode == 0:
        exe_path = current_dir / "dist" / f"{APP_NAME}.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 60)
            print(f"\n📁 Файл: {exe_path}")
            print(f"📊 Размер: {size_mb:.1f} MB")
            print("\n💡 Для запуска:")
            print("   1. Из корня проекта запустите backend: python run.py")
            print(f"   2. Запустите {APP_NAME}.exe")
            print("   .env остаётся в корне проекта и в exe не входит.")
        else:
            print("\n❌ Ошибка: .exe файл не найден")
            sys.exit(1)
    else:
        print("\n❌ Ошибка сборки")
        sys.exit(1)


def clean():
    """Очистить артефакты сборки, сохранив поддерживаемый spec."""
    current_dir = Path(__file__).parent
    
    dirs_to_remove = ["build", "dist", "__pycache__"]
    
    print("🧹 Очистка артефактов сборки...")
    print(f"   Spec-файл {SPEC_FILE} не удаляется — он нужен для сборки.")
    
    for dir_name in dirs_to_remove:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Удалено: {dir_name}/")
    
    print("✓ Очистка завершена")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean()
    else:
        build_exe()
