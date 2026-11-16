"""Independent Linux inotify capture and assessor-only process FD inspection."""
import ctypes
import os
from pathlib import Path
import struct

EVENT = struct.Struct("iIII")
OPEN, ACCESS, MOVED_TO, OVERFLOW = 0x20, 0x01, 0x80, 0x4000
MASK = OPEN | ACCESS | MOVED_TO


class Watch:
    def __init__(self, directory):
        libc = ctypes.CDLL(None, use_errno=True)
        self.fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1")
        if libc.inotify_add_watch(self.fd, os.fsencode(directory), MASK) < 0:
            os.close(self.fd)
            raise OSError(ctypes.get_errno(), "inotify_add_watch")

    def drain(self):
        result = []
        while True:
            try:
                page = os.read(self.fd, 65536)
            except BlockingIOError:
                return result
            offset = 0
            while offset < len(page):
                _, mask, _, size = EVENT.unpack_from(page, offset)
                offset += EVENT.size
                name = os.fsdecode(page[offset:offset + size].split(b"\x00", 1)[0])
                offset += size
                result.append({"name": name, "mask": mask})

    def close(self):
        os.close(self.fd)


def descriptor(pid, directory):
    base = Path("/proc") / str(pid)
    candidates = []
    for file in (base / "fd").iterdir():
        path = Path(file.readlink())
        if path.parent == directory and path.name.startswith("r@"):
            stat = file.stat()
            fields = dict(line.split(":", 1) for line in (base / "fdinfo" / file.name).read_text().splitlines())
            candidates.append({"file": path.name, "offset": int(fields["pos"]),
                               "inode": stat.st_ino, "dev": stat.st_dev, "size": stat.st_size})
    if len(candidates) != 1:
        raise ValueError("expected exactly one threshold descriptor")
    return candidates[0]


def accessed(events, label=None):
    return [event["name"] for event in events if event["mask"] & ACCESS
            and (label is None or event["name"].startswith(label))]
