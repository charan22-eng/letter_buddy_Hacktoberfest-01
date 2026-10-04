import time

from letterbuddy.privacy import purge_old_files_once


def test_auto_purge(tmp_path):
    # tmp_path is provided by pytest
    f1 = tmp_path / "old.wav"
    f2 = tmp_path / "new.wav"

    f1.write_text("old")
    f2.write_text("new")

    # Mock f1's mtime to 6 minutes ago
    six_mins_ago = time.time() - 360
    import os
    os.utime(f1, (six_mins_ago, six_mins_ago))

    # Mock f2's mtime to 1 minute ago
    one_min_ago = time.time() - 60
    os.utime(f2, (one_min_ago, one_min_ago))

    purge_old_files_once(tmp_path, max_age_seconds=300)

    assert not f1.exists()
    assert f2.exists()
