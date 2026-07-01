import shutil
import time
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

WATCH_FOLDER = Path(__file__).resolve().parent.parent / "watch_folder"
PROCESSED_FOLDER = WATCH_FOLDER / "processed"


class ImageHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(
            patterns=["*.jpg", "*.jpeg", "*.png"],
            ignore_directories=True,
            case_sensitive=False,
        )

    def on_created(self, event):
        src_path = Path(event.src_path)
        print(src_path.name)
        shutil.move(str(src_path), str(PROCESSED_FOLDER / src_path.name))


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
