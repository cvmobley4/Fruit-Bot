import shutil
import time
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from storage import save_result
from vision import analyze_image

WATCH_FOLDER = Path(__file__).resolve().parent.parent / "watch_folder"
PROCESSED_FOLDER = WATCH_FOLDER / "processed"


class ImageHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(
            patterns=["*.jpg", "*.jpeg", "*.png"],
            ignore_directories=True,
            case_sensitive=False,
        )
        self._in_progress = set()

    def on_created(self, event):
        src_path = Path(event.src_path)

        # Duplicate filesystem events for the same file are common (e.g. a
        # writer that creates then finalizes a file in separate steps), so
        # skip anything already handled or currently being handled.
        if src_path in self._in_progress or not src_path.exists():
            return
        self._in_progress.add(src_path)

        try:
            print(src_path.name)

            try:
                record = analyze_image(str(src_path))
            except Exception as exc:
                print(f"error analyzing {src_path.name}: {exc}")
                return

            print(f"fill_level: {record['fill_level']}")
            save_result(record)

            shutil.move(str(src_path), str(PROCESSED_FOLDER / src_path.name))
        finally:
            self._in_progress.discard(src_path)


def main():
    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(ImageHandler(), str(WATCH_FOLDER), recursive=False)
    observer.start()

    print(f"Watching {WATCH_FOLDER} for new images...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
