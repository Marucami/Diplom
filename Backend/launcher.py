import sys
import subprocess
import threading
import time
import os
from pathlib import Path

import webview

# ----------------------------------------------------------------------
# Определение базовой директории (где лежат исполняемые файлы PostgreSQL/Redis)
# ----------------------------------------------------------------------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent

BASE_DIR = get_base_dir()

# ----------------------------------------------------------------------
# Определение папки для данных PostgreSQL (постоянное место)
# ----------------------------------------------------------------------
def get_postgres_data_dir():
    if getattr(sys, 'frozen', False):
        # Для собранного приложения: %LOCALAPPDATA%\MoneyTracker\PostgreSQL\data
        appdata = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        data_dir = appdata / 'MoneyTracker' / 'PostgreSQL' / 'data'
    else:
        # Для разработки: рядом с проектом
        data_dir = BASE_DIR / 'PostgreSQL' / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# ----------------------------------------------------------------------
# Запуск портативного PostgreSQL
# ----------------------------------------------------------------------
def start_postgres():
    pg_bin = BASE_DIR / 'PostgreSQL' / 'bin'
    pg_ctl = pg_bin / 'pg_ctl.exe'
    initdb = pg_bin / 'initdb.exe'
    data_dir = get_postgres_data_dir()
    log_file = data_dir.parent / 'pg.log'

    # Инициализация кластера, если не инициализирован
    if not (data_dir / 'postgresql.conf').exists():
        print(f"Initializing PostgreSQL cluster in {data_dir}...")
        # Удаляем папку, если она не пустая (но не полностью, только если конфликтует)
        if data_dir.exists() and any(data_dir.iterdir()):
            print(f"Data directory {data_dir} is not empty. Removing contents...")
            import shutil
            shutil.rmtree(data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(initdb), '-D', str(data_dir), '-U', 'postgres', '--auth=trust'],
            check=True,
            capture_output=True,
            text=True
        )

    # Запуск PostgreSQL
    print("Starting PostgreSQL...")
    subprocess.Popen([str(pg_ctl), 'start', '-D', str(data_dir), '-l', str(log_file)])

# ----------------------------------------------------------------------
# Запуск портативного Redis (данные можно тоже вынести, но для простоты оставим временную папку)
# ----------------------------------------------------------------------
def start_redis():
    redis_exe = BASE_DIR / 'Redis' / 'redis-server.exe'
    # Для Redis можно задать постоянную папку для dump.rdb, но пока не критично
    subprocess.Popen([str(redis_exe)])

# ----------------------------------------------------------------------
# Остановка PostgreSQL
# ----------------------------------------------------------------------
def stop_postgres():
    pg_bin = BASE_DIR / 'PostgreSQL' / 'bin'
    pg_ctl = pg_bin / 'pg_ctl.exe'
    data_dir = get_postgres_data_dir()
    subprocess.run([str(pg_ctl), 'stop', '-D', str(data_dir)])

# ----------------------------------------------------------------------
# Запуск Django через waitress
# ----------------------------------------------------------------------
def run_django():
    print("Current sys.path:", sys.path)
    print("BASE_DIR:", BASE_DIR)
    print("Contents of BASE_DIR:", list(BASE_DIR.iterdir()))
    sys.path.insert(0, str(BASE_DIR))
    try:
        import money_tracker.wsgi
        print("wsgi imported successfully")
        from waitress import serve
        serve(money_tracker.wsgi.application, host='127.0.0.1', port=8000)
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        raise

# ----------------------------------------------------------------------
# Основная функция
# ----------------------------------------------------------------------
def main():
    start_postgres()
    start_redis()
    time.sleep(2)

    django_thread = threading.Thread(target=run_django, daemon=True)
    django_thread.start()
    time.sleep(3)

    webview.create_window(
        title='Money Tracker',
        url='http://127.0.0.1:8000',
        width=1280,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    webview.start(debug=False, http_server=True)

    stop_postgres()
    sys.exit(0)

if __name__ == '__main__':
    main()