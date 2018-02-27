# -*- coding: utf-8 -*-
import os
import pytsk3

# Following template from https://github.com/log2timeline/dfvfs/blob/master/dfvfs/file_io/tsk_file_io.py


class TskFileIo(object):
    """Class that implements a file-like object using pytsk3."""
    def __init__(self, tsk_file):
        """Initializes the file-like object.

        Args:
            tsk_file: the tsk File object
        """
        self.tsk_file = tsk_file
        self._current_offset = 0

    def read(self, size=None):
        """Implement the read functionality.

        Args:
            size: The size to read.
        Returns:
            bytes
        """

        if self._current_offset < 0:
            raise IOError(u'Invalid current offset value less than zero.')

        if self._current_offset >= self.tsk_file.info.meta.size:
            return b''

        if size is None or self._current_offset + size > self.tsk_file.info.meta.size:
            size = self.tsk_file.info.meta.size - self._current_offset

        data = self.tsk_file.read_random(
            self._current_offset, size
        )

        self._current_offset += len(data)

        return data

    def seek(self, offset, whence=os.SEEK_SET):
        """Seeks an offset within the file-like object.

        Args:
            offset: The offset to seek.
            whence: Optional value that indicates whether offset is an absolute or relative position within the file.
        """
        if whence == os.SEEK_CUR:
            offset += self._current_offset

        elif whence == os.SEEK_END:
            offset += self.tsk_file.info.meta.size
        elif whence != os.SEEK_SET:
            raise IOError(u'Unsupported whence.')

        if offset < 0:
            raise IOError(u'Invalid offset value less than zero.')

        self._current_offset = offset

    def get_offset(self):
        """Get the current offset.

        Returns:
            file offset
        """
        return self._current_offset

    def get_size(self):
        """Get the file's size.

        Returns:
            file size
        """
        return self.tsk_file_info.size

    def tell(self):
        """Alias for get_offset()

        Returns:
            file offset
        """
        return self.get_offset()
