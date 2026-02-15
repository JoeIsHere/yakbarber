"""Command-line interface for Yak Barber."""

import argparse
import cProfile
import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .settings import load_settings
from .engine import build

# Module-level state for debouncing
_debounce_timer = None
_is_running = False


class ChangeHandler(FileSystemEventHandler):
    """Watches content and template directories for changes and triggers rebuilds."""

    def __init__(self, settings):
        self._settings = settings
        self._lock = threading.Lock()

    def on_modified(self, event):
        if event.src_path.endswith(('.md', '.markdown')):
            print(f"Detected change in {event.src_path}. Scheduling rebuild...")
            self._schedule_build()

    def on_created(self, event):
        if event.src_path.endswith(('.md', '.markdown')):
            print(f"Detected new file {event.src_path}. Scheduling rebuild...")
            self._schedule_build()

    def _schedule_build(self):
        global _debounce_timer
        if _debounce_timer is not None:
            _debounce_timer.cancel()
        _debounce_timer = threading.Timer(3.0, self._run_build)
        _debounce_timer.start()

    def _run_build(self):
        global _is_running
        if not _is_running:
            _is_running = True
            try:
                with self._lock:
                    build(self._settings)
            finally:
                _is_running = False


def main():
    parser = argparse.ArgumentParser(
        description='Yak Barber is a fiddly little time sink, and blog system.'
    )
    parser.add_argument(
        '-s', '--settings', nargs=1,
        help='Specify a settings.toml file to use.'
    )
    parser.add_argument(
        '-c', '--cprofile', action='store_true', default=False,
        help='Run cProfile to check run time and elements.'
    )
    parser.add_argument(
        '-w', '--watch', action='store_true', default=False,
        help='Enable watchdog observer to monitor contentDir and templateDir.'
    )
    args = parser.parse_args()
    settings_path = args.settings[0] if args.settings else 'settings.toml'
    settings = load_settings(settings_path)

    if args.cprofile:
        cProfile.run('build(settings)', globals={'build': build, 'settings': settings})
    elif args.watch:
        observer = Observer(timeout=120)
        event_handler = ChangeHandler(settings)
        observer.schedule(event_handler, path=settings.content_dir, recursive=False)
        observer.schedule(event_handler, path=settings.template_dir, recursive=True)
        observer.start()
        try:
            build(settings)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        build(settings)


if __name__ == '__main__':
    main()
