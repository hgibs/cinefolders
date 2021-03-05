from pathlib import PurePath

from .videoid import VideoID

class FilePathTree:
    def __init__(self, rootPath, higher=None):
        """
        Initialize double-linked tree
        :param rootPath: PurePath object of root
        """
        if not isinstance(rootPath, PurePath):
            raise ValueError("rootPath must be a PurePath object")
        self.root = rootPath
        self.items = []
        self.ids = []
        self.higher = higher

    def isFile(self):
        return self.root.isFile()

    def addItem(self, item):
        if not isinstance(item, FilePathTree):
            raise ValueError("item must be a FilePathTree object")
        item.higher = self
        self.items.append(item)

    def addId(self, id):
        if not isinstance(id, VideoID):
            raise ValueError("item must be a Id object")
        self.ids.append(id)