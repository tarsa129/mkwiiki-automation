import json

from common_utils.track_page_utils.template_utils import misc_info_utils
from tockdomio.tockdomread_category import get_page_entries_of_supercategory

WRITE_BATCH_SIZE = 100

def get_wbz_id_from_page(category, skip_until, file):
    if not skip_until:
        with open(file, "w") as f:
            f.write('{\n"page_list": [')

    family_ids = []
    for page_entry in get_page_entries_of_supercategory(category):
        page_text: str = page_entry["revisions"][0]["slots"]["main"]["content"]
        try:
            misc_info = misc_info_utils.get_miscinfo_template(page_text)
            if misc_info is None or "wbz-id" not in misc_info:
                raise Exception()
            wbz_id = misc_info["wbz-id"]
            if not wbz_id:
                continue
            new_title = page_entry["title"].replace(" ", "_")
            family_ids.append({"page_id": page_entry["pageid"], "page_name": new_title, "wbzid_list": [int(wbz_id)]})
            if len(family_ids) % WRITE_BATCH_SIZE == WRITE_BATCH_SIZE - 1:
                with open(file, "a") as f:
                    f.write(json.dumps(family_ids, indent = 1)[1:-1])
                family_ids.clear()
        except:
            print("ERROR WITH ENTRY", page_entry)

    with open(file, "a") as f:
        f.write("]\n}")
