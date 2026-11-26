import hashlib
import logging

from constants import SZSLIB_TRACK_AUTHOR, SZSLIB_TRACK_EDITOR
from tockdomio import szslibrary_read
from tockdomio.szslibrary_read import get_image_from_id

class SZSLibraryTrackInfo:
    id_first = 0
    track_wiki = 0
    prefix = ""
    trackname = ""
    track_version = ""
    track_version_extra = ""
    track_author = set()
    track_editor = set()
    track_family = 0
    track_clan = 0
    track_sha1 = ""
    track_created = ""
    track_wbz_size = 0
    track_warn = 0
    track_slot = ""
    track_prop = ""
    track_music = ""
    track_speed = 1
    track_laps = 3
    track_customtrack = 0
    track_customarena = 0
    track_texturehack = 0
    track_boost = 0
    track_competition = 0
    track_nintendo = 0
    track_change = 0

    @classmethod
    def from_szslibrary_response(cls, dict_response):
        track_info = cls()
        track_info.__dict__ = dict_response

        track_info.track_author = set(dict_response[SZSLIB_TRACK_AUTHOR].split(","))
        track_info.track_version_extra = track_info.track_version_extra or None

        track_editor_text = dict_response[SZSLIB_TRACK_EDITOR]
        if track_editor_text is None:
            track_info.track_updaters = set()
        else:
            track_info.track_updaters = set(track_editor_text.strip().split(","))

        track_info.track_customtrack = str(track_info.track_customtrack) == "1"
        track_info.track_customarena = str(track_info.track_customarena) == "1"
        track_info.track_texturehack = str(track_info.track_texturehack) == "1"
        track_info.track_competition = str(track_info.track_competition) == "1"
        track_info.track_nintendo = str(track_info.track_nintendo) == "1"
        track_info.track_change = str(track_info.track_change) == "1"

        return track_info

    def get_mod_type(self):
        if self.track_change:
            return "Edit"
        elif self.track_texturehack:
            return "Texture"
        return None

    def is_official_version(self):
        return self.track_version_extra is None

    def get_expected_page_prefix(self):
        base = self.get_full_trackname()
        if mod_type := self.get_mod_type():
            if self.track_nintendo and self.track_prop:
                base += f" ({track_prop_to_track(self.track_prop)} {mod_type})"
            elif not self.track_nintendo and self.track_clan:
                base_track = get_track_info(self.track_clan)
                if not base_track:
                    logging.warning(f"{base}'s clan of {self.track_clan} is not valid!")
                else:
                    base += f" ({base_track.get_full_trackname()} {mod_type})"
        return base.replace("_", "")

    def get_full_trackname(self):
        track_name = f"{self.trackname}".strip()
        prefix = self.prefix
        if prefix:
            track_name = f"{prefix} {track_name}"
        return track_name

    def get_full_versionname(self):
        version_name = f"{self.track_version}".strip()
        version_extra = self.track_version_extra
        if version_extra:
            version_name = f"{version_name}-{version_extra}"
        return version_name

    def get_full_trackname_version(self):
        track_name = self.get_full_trackname()
        version_name = self.get_full_versionname()
        return f"{track_name} {version_name}"

    def get_writeable_entry(self):
        return {"wbz_id": self.track_family, "image_id": self.id_first,
                "page_id": self.track_wiki, "track_name": self.get_full_trackname(), "track_version_extra": self.get_full_versionname(),
                "authors": self.track_author, "updaters": self.track_editor}

track_prop_lookup = {
    0x08: "Luigi Circuit", 0x01: "Moo Moo Meadows", 0x02: "Mushroom Gorge", 0x04: "Toad's Factory",
    0x00: "Mario Circuit", 0x05: "Coconut Mall", 0x06: "DK Summit", 0x07: "Wario's Gold Mine",
    0x09: "Daisy Circuit", 0x0f: "Koopa Cape", 0x0b: "Maple Treeway", 0x03: "Grumble Volcano",
    0x0e: "Dry Dry Ruins", 0x0a: "Moonview Highway", 0x0c: "Bowser's Castle", 0x0d: "Rainbow Road",
    0x10: "GCN Peach Beach", 0x14: "DS Yoshi Falls", 0x19: "SNES Ghost Valley 2", 0x1a: "N64 Mario Raceway",
    0x1b: "N64 Sherbet Land", 0x1f: "GBA Shy Guy Beach", 0x17: "DS Delfino Square", 0x12: "GCN Waluigi Stadium",
    0x15: "DS Desert Hills", 0x1e: "GBA Bowser Castle 3", 0x1d: "N64 DK's Jungle Parkway", 0x11: "GCN Mario Circuit",
    0x18: "SNES Mario Circuit 3", 0x16: "DS Peach Gardens", 0x13: "GCN DK Mountain", 0x1c: "N64 Bowser's Castle",
    0x21: "Block Plaza", 0x20: "Delfino Pier", 0x23: "Funky Stadium", 0x22: "Chain Chomp Wheel", 0x24: "Thwomp Desert",
    0x27: "SNES Battle Course 4", 0x28: "GBA Battle Course 3", 0x29: "N64 Skyscraper", 0x25: "GCN Cookie Land", 0x26: "DS Twilight House"
}

def track_prop_to_track(track_prop):
    track_prop = int(track_prop)
    return track_prop_lookup.get(int(track_prop), None)

def validate_wbz_id(id_text):
    if not id_text.isnumeric():
        return False

    id_num = int(id_text)
    if id_num == 0:
        return False

    return True

def validate_start_end_wbz_ids(start_id, end_id):
    if not validate_wbz_id(start_id):
        raise RuntimeError(f"Start id {start_id} must be a positive integer")
    if not validate_wbz_id(end_id):
        raise RuntimeError(f"End id {end_id} must be a positive integer")

    start_id_num = int(start_id)
    end_id_num = int(end_id)

    if end_id_num < start_id_num:
        raise RuntimeError(f"Start id {start_id_num} cannot be greater than end id {end_id}")

    return True

def get_track_info(wbz_id):
    szslibrary_response = szslibrary_read.get_by_wbz_id(wbz_id)
    if not szslibrary_response or not szslibrary_response.get("track_info", None):
        return None

    return SZSLibraryTrackInfo.from_szslibrary_response(szslibrary_response["track_info"])

def get_family_info(family_id):
    szslibrary_response = szslibrary_read.get_by_family_id(family_id)
    if not szslibrary_response or not szslibrary_response.get("tracks", None):
        return None

    tracks = []
    for track in szslibrary_response["tracks"]:
        tracks.append(SZSLibraryTrackInfo.from_szslibrary_response(track))

    return tracks

def get_imagehash_by_id(image_id):
    image_content = get_image_from_id(image_id)
    if image_content is None:
        return None

    return hashlib.sha256(str(image_content).encode()).hexdigest()