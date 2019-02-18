from collections import namedtuple

_picture_fields = ("name", "source_url", "type", "season", "episode",)
Picture = namedtuple("Picture", _picture_fields, defaults=(None, ) * len(_picture_fields))
