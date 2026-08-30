from pathlib import Path

from backend.app.documents.storage import LocalStorage


def test_local_storage_persists_and_resolves_across_instances(tmp_path: Path):
    first_instance = LocalStorage(str(tmp_path))
    storage_reference = first_instance.save("../college handbook?.txt", b"official content")

    second_instance = LocalStorage(str(tmp_path))

    assert Path(storage_reference).read_bytes() == b"official content"
    assert Path(second_instance.resolve(storage_reference)).read_bytes() == b"official content"

    second_instance.delete(storage_reference)
    assert not Path(storage_reference).exists()
