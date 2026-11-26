import logging

from common_utils.szslibrary_helpers import SZSLibraryTrackInfo
from common_utils.track_page_utils.template_utils.misc_info_utils import get_miscinfo_template
from common_utils.track_page_utils.wiiki_name_utils.match_page_to_track import parse_page_name
from mediawiki.mediawiki_read import clean_text
from tockdomio import tockdomread
from tockdomio.tockdom_search import search_by_page_name

# Without checking what the track is a modification of (e.g. "Rainbow Road Edit" vs "Luigi Circuit Edit")
# This will fail for same-named, same-typed, same-authored tracks of different origins.
# Such a case is hopefully rare.
def full_page_check(page_id, mod_type, authors):
    tockdom_response = tockdomread.get_page_text_by_id(page_id) #guaranteed to exist, minus some edge case where page is deleted

    # Check for misc-info (for confirmation of this being an actual track page, not a disambiguation)
    misc_info = get_miscinfo_template(tockdom_response["revisions"][0]["slots"]["main"]["content"])
    if misc_info is None:
        return False

    # Strict check for equality of authors
    misc_info_authors = misc_info["author"] if "author" in misc_info and misc_info["author"] else misc_info["creator"]
    if misc_info_authors is None and authors:
        return False

    page_authors = set(clean_text(misc_info_authors).split(", "))
    if page_authors != authors:
        return False

    # Check type of track (for mod type)
    for category in tockdom_response["categories"]:
        if category["title"].endswith("/Edit") and mod_type != "Edit":
            return False
        if category["title"].endswith("/Texture") and mod_type != "Texture":
            return False

    return True

def get_page_from_track_info(track_info: SZSLibraryTrackInfo):
    page_id, page_title, failed_ids = find_track_page_with_name_prefix(track_info, track_info.get_expected_page_prefix().lower())
    if page_id:
        return page_id, page_title
    page_id, page_title, _ = find_track_page_with_name_prefix(track_info, track_info.get_full_trackname().replace("_", " ").lower(), failed_ids)
    return page_id, page_title

def find_track_page_with_name_prefix(track_info: SZSLibraryTrackInfo, name_prefix, already_failed=None):
    # Currently does not filter out custom characters/vehicles.
    # This would probably fail for some niche Factory Island edge case.
    if already_failed is None:
        already_failed = set()
    valid_names = [(page["pageid"], page["title"]) for page in search_by_page_name(name_prefix) if page["title"].lower().startswith(name_prefix)]
    logging.info(f"For {track_info.id_first} page {track_info.get_expected_page_prefix()} found {len(valid_names)} valid pages.")

    # if literally only one page starts with the required text, it's probably okay.
    if len(valid_names) == 1:
        return valid_names[0][0], valid_names[0][1], None

    base_name, mod_type, authors = track_info.get_full_trackname().replace("_", " "), track_info.get_mod_type(), track_info.track_author
    failed_ids = set()
    for page_id, page_title in valid_names:
        if already_failed and page_id in already_failed:
            continue

        track_page_parse = parse_page_name(page_title, base_name)
        if not track_page_parse:
            logging.warning(f"page name {page_title} cannot be parsed")
            failed_ids.add(page_id)
            continue
        if not track_page_parse.check_with_track(base_name, mod_type, authors):
            failed_ids.add(page_id)
            continue

        if full_page_check(page_id, mod_type, authors):
            return page_id, page_title, None

    return None, None, failed_ids

