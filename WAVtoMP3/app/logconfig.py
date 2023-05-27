import logging
import os
import sys


class PackagePathFilter(logging.Filter):
    """
    class for writing relative path in logs
    """
    def filter(self, record: logging.LogRecord) -> bool:
        """
        gets relative path from absolute
        """
        pathname: str = record.pathname
        record.relativepath = None
        abs_sys_paths: map = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = os.path.relpath(pathname, path)
                break
        return True
