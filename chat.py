import re
import requests
from bs4 import BeautifulSoup

from os import system
import platform
import time
from typing import Union


class CookieInvalid(Exception):
    """Cookie Invalid Exception"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class Chat(requests.Session):

    def __init__(self, cookie: str):
        super().__init__()
        self.cookie = {"cookie": cookie}
        self.headers.update(
            {
                "Host": "mbasic.facebook.com",
                "Cookie": cookie,
            }
        )

    def response(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self.get(url, cookies=self.cookie).text, "html.parser")

    def pesan(self, uid: str, message: str, photo: dict):
        pesan_response = self.get_pesan_response(uid=uid)

        if pesan_response is False:
            print(f" #~ Send Message Faileddd! - {uid}")

        else:

            data_message, data_photo = (
                pesan_response["message"],
                pesan_response["photo"],
            )

            data_message["data"]["body"] = message
            send_pesan = self.send_pesan(
                uid=uid,
                data=data_message["data"],
                action=data_message["action"],
                referer=pesan_response["referer"],
            )
            send_photo = self.send_photo(
                url=data_photo["action"],
                data=data_photo["data"],
                files=photo,
            )

            if send_pesan or send_photo:
                print(f" #~ Send Message Success! - {uid}")
            else:
                print(f" #~ Send Message Faileddd! - {uid}")

    def send_photo(self, url: str, data: dict, files: dict) -> bool:
        post = self.post(
            url,
            data=data,
            files=files,
            cookies=self.cookie,
        )

        if post.status_code != 200:
            return False

        return True

    def send_pesan(self, uid: str, data: str, action: str, referer: str) -> bool:
        post = self.post(
            f"https://mbasic.facebook.com{action}",
            data=data,
            cookies=self.cookie,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": referer,
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            },
        )

        if post.status_code != 200:
            return False

        return True

    def get_pesan_response(self, uid: str) -> Union[dict, bool]:
        soup = self.response(f"https://mbasic.facebook.com/messages/compose/?ids={uid}")
        if "mbasic_logout_button" not in str(soup):
            raise CookieInvalid("Cookie Akun Invalid!!")

        try:
            # data message
            composer_form = soup.find("form", attrs={"id": "composer_form"})
            data_message = {
                inp.get("name"): inp.get("value")
                for inp in composer_form.findAll(
                    "input", attrs={"name": True, "value": True}
                )
            }

            # data photo
            photo_form = soup.find(
                "form",
                attrs={
                    "action": re.compile(
                        "(https\:\/\/upload\.facebook\.com\/\_mupload\_\/mbasic\/messages\/attachment\/photo.*?)"
                    )
                },
            )
            data_photo = {
                inp.get("name"): inp.get("value")
                for inp in photo_form.findAll(
                    "input", attrs={"name": True, "value": True}
                )
            }

            return {
                "message": {"data": data_message, "action": composer_form["action"]},
                "photo": {
                    "data": data_photo,
                    "action": photo_form["action"],
                },
                "referer": f"https://mbasic.facebook.com/messages/compose/?eav=AfYxgVxkaUT2guTrwmu8ar2LftDmZu2I976VfHJ6F3KPuh3ENhyCPcMVgiej30GwvrY&paipv=0&ids={uid}",
            }
        except Exception:
            return False


def Login(cookie: str) -> Union[dict, bool]:
    response = BeautifulSoup(
        requests.get("https://mbasic.facebook.com/me", cookies={"cookie": cookie}).text,
        "html.parser",
    )
    if "mbasic_logout_button" not in str(response):
        return False

    return {"name": response.title.string}


def main():
    print(" Login Dulu Bang :D")
    cookie = input(" cookie: ")
    id = "".join(re.findall("c_user=(\d+);", cookie))
    me = Login(cookie=cookie)

    if me is False:
        raise CookieInvalid("[Cookie Invalid] Cookie Akun Invalid!")

    system("cls" if platform.system() == "Windows" else "clear")

    print(" #~ Welcome to Script ~# ")
    print("")
    print(f" $ Uid: {id}")
    print(f" $ Name: {me['name']}")
    print("")

    # path file list account
    print(" @ Path File list akun ")
    accounts = input(" >> file list akun: ")
    try:
        accounts = open(accounts, "r").readlines()
    except FileNotFoundError:
        raise FileNotFoundError("[List Akun] File Tidak Ada!")

    # message
    print(" @ Use '\\n' for line break")
    message = input(" >> isi pesan: ").split("|")

    # path file photo
    print(" ? Add gambar")
    t_photo = input(" >> y/n: ")
    if t_photo.lower() == "y":
        print(" @ Path File photo (max: 4) ")
        d_photo = []
        j_photo = int(input(" >> jumlah photo: "))
        for i in range(j_photo):
            photo = input(f" >> {i+1} file photo: ")
            d_photo.append(photo)

    # delay message
    print(" @ Delay in seconds")
    delay = int(input(" >> delay message: "))

    print("")

    len_account = 0
    Start = Chat(cookie=cookie)
    for account in accounts:
        data = (
            {f"file{i+1}": open(photo, "rb") for i, photo in enumerate(d_photo)}
            if t_photo.lower() == "y"
            else None
        )
        account = account.replace("\n", "")
        if len_account == len(message):
            len_account = 0
        Start.pesan(uid=account, message=message[len_account], photo=data)
        time.sleep(delay)

        len_account += 1


if __name__ == "__main__":
    main()
