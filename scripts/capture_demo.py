"""Captures clean README screenshots and a short demo video."""

import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
SCREENSHOT_FOLDER = PROJECT_FOLDER / "assets" / "screenshots"
DEMO_FOLDER = PROJECT_FOLDER / "assets" / "demo"
DEMO_SOURCE_FOLDER = Path("/tmp/neatify-demo-folder")

sys.path.insert(0, str(PROJECT_FOLDER))

from window import NeatifyWindow


def create_demo_folder():
    if DEMO_SOURCE_FOLDER.exists():
        shutil.rmtree(DEMO_SOURCE_FOLDER)

    DEMO_SOURCE_FOLDER.mkdir(parents=True)

    for folder_name in ["Class Notes", "Screenshots", "Projects"]:
        (DEMO_SOURCE_FOLDER / folder_name).mkdir()

    demo_files = {
        "microeconomics_notes.pdf": "Fake PDF content",
        "array_practice.py": "print('arrays')",
        "campus_photo.jpg": "Fake image content",
        "lecture_clip.mp4": "Fake video content",
        "budget.csv": "item,cost\nbooks,40",
        "archive_backup.zip": "Fake archive content",
    }

    for file_name, contents in demo_files.items():
        (DEMO_SOURCE_FOLDER / file_name).write_text(contents, encoding="utf-8")


def prepare_output_folders():
    SCREENSHOT_FOLDER.mkdir(parents=True, exist_ok=True)
    DEMO_FOLDER.mkdir(parents=True, exist_ok=True)


def set_window_to_demo_folder(window):
    window.state.selected_folder_name = "Demo Folder"
    window.state.selected_folder_path = str(DEMO_SOURCE_FOLDER)
    window.state.current_view_folder_path = str(DEMO_SOURCE_FOLDER)
    window.state.current_arrange_folder_path = str(DEMO_SOURCE_FOLDER)

    window.folder_name_label.setText("Demo Folder")
    window.breadcrumb_label.setText(str(DEMO_SOURCE_FOLDER))
    window.folder_summary_label.setText(window.get_folder_status(str(DEMO_SOURCE_FOLDER)))
    window.update_folder_cards()
    window.update_folder_contents_list(str(DEMO_SOURCE_FOLDER))


def save_window(window, file_name):
    QApplication.processEvents()
    pixmap = window.grab()
    pixmap.save(str(SCREENSHOT_FOLDER / file_name))


def create_demo_video():
    frame_paths = [
        SCREENSHOT_FOLDER / "01-main-window.png",
        SCREENSHOT_FOLDER / "02-arrange-preview.png",
        SCREENSHOT_FOLDER / "03-after-organize.png",
        SCREENSHOT_FOLDER / "04-history.png",
    ]

    video_path = DEMO_FOLDER / "neatify-demo.mp4"
    concat_file = DEMO_FOLDER / "frames.txt"

    lines = []

    for frame_path in frame_paths:
        lines.append("file '" + str(frame_path) + "'")
        lines.append("duration 2")

    lines.append("file '" + str(frame_paths[-1]) + "'")

    concat_file.write_text("\n".join(lines), encoding="utf-8")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-vf",
            "format=yuv420p",
            "-movflags",
            "+faststart",
            str(video_path),
        ],
        check=True,
    )

    return video_path


def main():
    prepare_output_folders()
    create_demo_folder()

    app = QApplication(sys.argv)
    window = NeatifyWindow()
    window.resize(1100, 680)
    window.show()
    QApplication.processEvents()

    set_window_to_demo_folder(window)
    save_window(window, "01-main-window.png")

    window.show_arrange_preview(str(DEMO_SOURCE_FOLDER))
    save_window(window, "02-arrange-preview.png")

    window.organize_selected_folder()
    save_window(window, "03-after-organize.png")

    window.show_history()
    save_window(window, "04-history.png")

    video_path = create_demo_video()
    print("Saved screenshots in:", SCREENSHOT_FOLDER)
    print("Saved demo video:", video_path)

    app.quit()


if __name__ == "__main__":
    main()
