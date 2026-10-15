from common_utils.track_page_utils.template_utils import misc_info_utils
from tockdomio.tockdomread_category import get_page_entries_of_supercategory


def get_wbz_id_from_page(category, skip_until, file):
    if not skip_until:
        with open(file, "w") as f:
            f.write('{\n"page_list": [\n')

    family_ids = []
    i = 0
    for page_entry in get_page_entries_of_supercategory(category):
        page_text: str = page_entry["revisions"][0]["slots"]["main"]["content"]
        wbz_id = misc_info_utils.get_miscinfo_template(page_text)["wbz-id"]
        new_title = page_entry["title"].replace(" ", "_")
        family_ids.append({"page_id": page_entry["pageid"], "page_name": new_title, "wbzid_list": [wbz_id]})
        break
    with open(file, "a") as f:
        f.write("]\n}")
