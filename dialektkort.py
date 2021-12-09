from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import folium
from folium.plugins import MarkerCluster


dialekter = []


def manual_correction(sogn):
    if sogn == "svanneke":
        sogn = "svaneke"

    if sogn == "åkirkeby":
        sogn = "aaker"

    if sogn == "skagen landsogn":
        sogn = "skagen"

    if sogn == "stepping by":
        sogn = "stepping"

    if sogn == "øster lars":
        sogn = "østerlarsker"

    if sogn == "aså-melholt":
        sogn = "asaa"

    if sogn == "trøstrup-korup":
        sogn = "korup"

    if sogn == "højer flække":
        sogn = "højer"

    if sogn == "vålse":
        sogn = "nordvestfalster"

    if sogn == "asserballeskov":
        sogn = "asserballe"

    if sogn == "ø. højst":
        sogn = "højst"

    if sogn == "øster marie":
        sogn = "østermarie"

    if sogn == "åbenrå by":
        sogn = "åbenrå"

    if sogn == "gøl":
        sogn = "gjøl"

    if sogn == "grønholt-asminderød":
        sogn = "grønholt"

    if sogn == "klemmensker":
        sogn = "klemensker"

    if sogn == "tavlov":
        sogn = "taulov"

    if sogn == "thorkilstrup":
        sogn = "torkilstrup"

    if sogn == "haubro":
        sogn = "havbro"

    if sogn == "ny sogn":
        sogn = "nysogn"

    if sogn == "k. hyllinge":
        sogn = "kirke hyllinge"

    if sogn == "kirke-stilling":
        sogn = "kirke stillinge"

    if sogn == "fløstrup":
        sogn = "flødstrup"

    if sogn == "ingslev":
        sogn = "indslev"

    if sogn == "poulsker":
        sogn = "povlsker"

    if sogn == "harboør":
        sogn = "harboøre"

    if sogn == "allese":
        sogn = "allesø"

    if sogn == "ribe land":
        sogn = "ribe"

    if sogn == "torstrup":
        sogn = "thorstrup"

    if sogn == "oddum":
        sogn = "ådum"

    if sogn == "flække-sandvig":
        sogn = "sandvig"

    if sogn == "rorslev":
        sogn = "roerslev"

    if sogn == "bure":
        sogn = "bur"

    if sogn == "rær":
        sogn = "ræhr"

    if sogn == "sandholt-lyndelse":
        sogn = "sandholts lyndelse"

    if sogn == "glæsborg":
        sogn = "glesborg"

    return sogn


def sogn_to_coordinates(sogn):
    sogn = sogn.lower()
    sogn = sogn.replace(" landsogn", "")
    sogn = sogn.replace(" skovsogn", "")
    sogn = sogn.replace(" flække", "")

    sogn = manual_correction(sogn)

    url = f"https://api.dataforsyningen.dk/sogne?q={sogn}&per_side=1"
    req = requests.get(url)

    coordinates = req.json()[0]["visueltcenter"]
    return coordinates


sogn_coords = {}


pbar = tqdm(range(273))
for page in pbar:

    pbar.set_description(f"Scraping page {page+1}")
    html_doc = requests.get(
        f"https://dansklyd.statsbiblioteket.dk/samling/dialektsamlingen/?side={page+1}"
    ).text
    soup = BeautifulSoup(html_doc, "html.parser")

    h2_list = soup.find_all("h2", class_="kaltura-title")

    for sound_recording in h2_list:
        title = sound_recording.text.strip()
        link = sound_recording.find("a")["href"]
        sogn = title.split("sogn,")[0].split("fra")[1].strip()

        if not sogn in sogn_coords:
            sogn_coords[sogn] = sogn_to_coordinates(sogn)
            already_found = False
        else:
            already_found = True

        coordinates = sogn_coords[sogn]

        recording_data = {
            "title": title,
            "link": f"https://dansklyd.statsbiblioteket.dk{link}",
            "sogn": sogn,
            "coordinates": coordinates,
        }

        dialekter.append(recording_data)

        pbar.write(f"Title: {title}")
        pbar.write(f"Link: {link}")
        pbar.write(f"Sogn: {sogn}")
        pbar.write(
            f"Coordinates: {coordinates}{(' (Already found)' if already_found else '')}"
        )
        pbar.write(60 * "-")


m = folium.Map(location=[55.9396761, 9.5155848], zoom_start=7)
marker_cluster = MarkerCluster().add_to(m)

for i in dialekter:
    info = f"<b>{i['title']}</b><br><br><a href=\"{i['link']}\">Gå til optagelse</a>"
    folium.Marker([i["coordinates"][1], i["coordinates"][0]], popup=info).add_to(
        marker_cluster
    )

marker_cluster = MarkerCluster().add_to(m)

map_file = "dialektkort.html"
m.save(map_file)
print(f"\nMap saved to {map_file}\n")
