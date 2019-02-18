from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from pictures import models
from pictures.types import Picture


class BaseParser:
    def get_sources(self, name: str) -> List[Picture]:
        """Returns source attribute for i-frame tag for given season and episode
        for picture with name

        Attributes:
            name -- picture name separated by underscores (e.g. "doctor_house")
        """
        raise NotImplementedError("Implement in subclass")


class YandexParser(BaseParser):
    # Todo: Rewrite using Scrapy
    initial_name: str

    def __init__(self):
        self.base_url = "https://yandex.ru/video/"
        self.search_url = urljoin(self.base_url, "search")
        self.series_url_pattern = urljoin(
            self.base_url,
            "запрос/сериал/{film_name}/{season}-сезон/{episode}-серия?source=series_nav",
        )

    def get_sources(self, name: str) -> List[Picture]:
        """Returns sources for picture name"""
        page = requests.get(self.search_url, params={"text": name})
        soup = BeautifulSoup(page.text, "html.parser")
        self.initial_name = name
        if self._get_type_of_soup(soup) == models.Picture.SERIES:
            return self._parse_series(soup)
        else:
            return self._parse_films(name, soup)

    def _get_type_of_soup(self, soup) -> str:
        if soup.find("div", class_="series-navigator__main"):
            return models.Picture.SERIES
        else:
            return models.Picture.FILM

    def _parse_films(self, name: str, initial_page: BeautifulSoup) -> List[Picture]:
        """Parses film from yandex.video service

        Attributes:
            name         -- name of film
            initial_page -- page received from search
        """
        source = initial_page.find("iframe").get("src")
        return [Picture(name=name, source_url=f"http:{source}", type=models.Picture.FILM, episode=1, season=1)]

    def _parse_series(self, initial_page: BeautifulSoup) -> List[Picture]:
        """Parses all episodes from all seasones from Yandex.Video

        Attributes:
            initial_page -- Page to start from, should be result of yandex.video/search page.
        """
        season_selector = "label.carousel__item"
        seasons_count = len(initial_page.select(season_selector))
        internal_name = self._get_internal_series_name(initial_page)
        parsed_series = [
            episode for season in range(1, seasons_count + 1)
            for episode in self._series_parser(internal_name, season)
        ]
        return parsed_series

    @staticmethod
    def _get_internal_series_name(initial_page: BeautifulSoup) -> str:
        """Returns internal name of picture, consumed by get yandex.video request

        Attributes:
            initial_page -- Page to parse from, same as in self.parse_series method
        """
        name_selector = ".series-navigator__title-link"
        name_tag = initial_page.select(name_selector)[0]
        return name_tag.get_text().strip().replace(" ", "-").lower()

    def _parse_source(self, internal_name, season, episode) -> Picture:
        """Parses source data from yandex.video

        Attributes:
            internal_name    -- internal name
            season           -- season
            episode          -- episode
        """
        sources_url = self.series_url_pattern.format(film_name=internal_name, season=season, episode=episode)
        source = requests.get(sources_url)
        soup = BeautifulSoup(source.text, "html.parser")
        source_url = soup.find("iframe").get("src")
        return Picture(
            name=internal_name,
            source_url=f"http:{source_url}",
            type=models.Picture.SERIES,
            season=season,
            episode=episode,
        )

    def _series_parser(self, internal_name, season):
        """Generator to parse all series into array

        Attributes:
            internal_name -- internal yandex.video name of picture
            season        -- given season
        """
        episode_selector = "div.radio-table__list-row > label > span"
        start_url = self.series_url_pattern.format(film_name=internal_name, season=season, episode=1)
        start_page = requests.get(start_url)
        soup = BeautifulSoup(start_page.text, "html.parser")
        for episode_tag in soup.select(episode_selector):
            try:
                episode = int(episode_tag.get_text())
                yield self._parse_source(internal_name, season, episode)
            except ValueError:
                break

