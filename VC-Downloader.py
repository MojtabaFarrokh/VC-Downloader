########################################################################
#                                                                      #
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, version 3.                             #
#                                                                      #
# This program is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU     #
# General Public License for more details.                             #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# *along with this program. If not, see <http://www.gnu.org/licenses/>.#
########################################################################

import os.path

from bs4 import BeautifulSoup
import requests
import re
from tqdm import tqdm
import pwinput
import sys


def downloader(input):
    filename = input[0]
    link = input[1]
    s = input[2]
    r = s.get(link, stream=True)
    total_size_in_bytes = int(r.headers.get("content-length"))
    block_size = 1024

    if os.path.exists(filename) and os.path.getsize(filename) == total_size_in_bytes:
        print(f"{filename} has already been downloaded!")
    else:
        progress_bar = tqdm(
            total=total_size_in_bytes, unit="iB", unit_scale=True, desc=filename
        )
        with open(filename, "wb") as file:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()


if __name__ == "__main__":
    print(
        """Simple App for downloading mp4 from vc.kntu.ac.ir. :)
    Written by: Hoorad Farrokh and Mojtaba Farrokh"""
    )
    # Use 'with' to ensure the session context is closed after use.
    Video_url = input("Enter the url of the page that contains videos link:\n")
    login = input("Enter your username:")
    passwd = pwinput.pwinput("Enter password:", mask="*")
    if sys.platform == "win32":
        import certifi_win32

        os.environ["REQUESTS_CA_BUNDLE"] = certifi_win32.wincerts.where()
        certifi_win32.generate_pem()

    with requests.Session() as s:
        r = s.get(Video_url.split("mod")[0] + "login/index.php")
        cookie = r.cookies.get_dict()
        pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(pattern, r.text)
        # print(token)
        token = re.findall("\w{32}", token[0])
        payload = {
            "username": login,
            "password": passwd,
            "anchor": "",
            "logintoken": token[0],
        }

        p = s.post(
            Video_url.split("mod")[0] + "login/index.php",
            cookies=r.cookies,
            data=payload,
        )

        # print the html returned or something more intelligent to see if it's a successful login page.

        # create response object
        r = s.get(Video_url, cookies=p.cookies)
        # create beautiful-soup object
        soup = BeautifulSoup(r.content, "html5lib")

        # find all links on web-page
        links = soup.findAll("a")
        # filter the link ending with .mp4
        video_links = [
            Video_url.split("view")[0] + link["href"]
            for link in links
            if "mp4" in link["href"]
        ]
        temp = []
        for i in range(len(video_links)):
            temp.append((f"session {i+1}.mp4", video_links[i], s))
        print(f"Number of sessions to be downloaded is {len(temp)}.")
        for tt in temp:
            downloader(tt)
