import os
from typing import List
import random
import time
from datetime import datetime, timedelta, timezone

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import telegram
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "143976735"
TIMER = 10
TIMER_EXCEPTION = 600


class NineGagScraper:
    URL = "https://9gag.com/"

    def _get_main_page(self) -> str:
        browser = webdriver.Firefox()
        browser.get(self.URL)
        # проматываем страницу, чтобы получить загрузить post_views
        y_scroll = 100
        count_scroll = 300
        for _ in range(count_scroll):
            y_scroll = y_scroll + 100
            browser.execute_script(f"window.scrollTo(0, {y_scroll})")
            time.sleep(0.1)
        main_page = browser.page_source
        browser.quit()
        return main_page

    def _get_urls_imges_from_posts_views(self, posts_views) -> List[str]:
        urls_images = []
        for post_view in posts_views:
            picture_node = post_view.find("picture")
            source_node = picture_node.find("source")
            image_node = source_node.find("img")
            urls_images.append(image_node["src"])
        return urls_images

    def _get_urls_images(self):
        main_page = self._get_main_page()
        print(type(main_page))
        soup = BeautifulSoup(main_page, "lxml")
        posts_views = soup.find_all("div", class_="image-post post-view")

        return self._get_urls_imges_from_posts_views(posts_views)

    def get_random_url_image(self) -> str:
        urls_images = self._get_urls_images()
        return random.choice(seq=urls_images)


def is_message_old(message):
    now = datetime.now(timezone.utc)
    date_message = message.date
    delta = now - date_message
    result = delta > timedelta(seconds=TIMER)
    return result


def send_meme(bot: telegram.Bot, url_photo: str):
    bot.send_photo(chat_id=CHAT_ID, photo=url_photo)


def main():
    nineGAG = NineGagScraper()
    bot = telegram.Bot(TELEGRAM_TOKEN)
    while True:
        try:
            message = bot.get_updates(
                timeout=TIMER, allowed_updates=["message"], limit=1
            )[0].message

            if not message or is_message_old(message):
                send_meme(bot, nineGAG.get_random_url_image())
                time.sleep(TIMER)

        except Exception as e:
            print(e)
            time.sleep(TIMER_EXCEPTION)


if __name__ == "__main__":
    main()
