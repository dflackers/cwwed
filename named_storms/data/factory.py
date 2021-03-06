import os
import re
import celery
import pytz
import requests
from datetime import datetime, timedelta
from lxml import etree
from typing import List
from io import BytesIO
from urllib import parse
from named_storms import tasks
from named_storms.data.processors import ProcessorData
from named_storms.models import CoveredDataProvider, NamedStorm, NamedStormCoveredData


class ProcessorFactory:
    _named_storm: NamedStorm = None
    _provider: CoveredDataProvider = None
    _verify_ssl = True
    _provider_url_parsed = None
    _named_storm_covered_data: NamedStormCoveredData = None

    def __init__(self, storm: NamedStorm, provider: CoveredDataProvider):
        self._named_storm = storm
        self._provider = provider
        self._provider_url_parsed = parse.urlparse(self._provider.url)
        self._named_storm_covered_data = self._named_storm.namedstormcovereddata_set.get(covered_data=self._provider.covered_data)

    def processors_data(self) -> List[ProcessorData]:
        return [
            ProcessorData(
                named_storm_id=self._named_storm.id,
                provider_id=self._provider.id,
                url=self._provider.url,
                label=None,
            )
        ]


class NDBCProcessorFactory(ProcessorFactory):
    """
    https://dods.ndbc.noaa.gov/
    The NDBC has a THREDDS catalog which includes datasets for each station where the station format is 5 characters, i.e "20cm4".
    The datasets inside each station includes historical data and real-time data (45 days).  There is no overlap.
        - Historical data is in the format "20cm4h2014.nc"
        - "Real-time" data is in the format "20cm4h9999.nc"
    NOTE: NDBC's SSL certs aren't validating, so let's just not verify.
    """
    RE_PATTERN = re.compile(r'^(?P<station>\w{5})\w(?P<year>\d{4})\.nc$')
    # number of days "real-time" data is stored separately from the timestamped files
    REALTIME_DAYS = 45
    # "real-time" year format of file
    REALTIME_YEAR = 9999

    _verify_ssl = False

    def processors_data(self) -> List[ProcessorData]:
        station_urls = []
        dataset_paths = []
        processors_data = []

        namespaces = {
            'catalog': 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0',
            'xlink': 'http://www.w3.org/1999/xlink',
        }

        # parse the main catalog and iterate through the individual buoy stations
        catalog_response = requests.get(self._provider.url, verify=self._verify_ssl)
        catalog_response.raise_for_status()
        catalog = etree.parse(BytesIO(catalog_response.content))

        # build a list of all station catalog urls
        for catalog_ref in catalog.xpath('//catalog:catalogRef', namespaces=namespaces):
            dir_path = os.path.dirname(self._provider.url)
            href_key = '{{{}}}href'.format(namespaces['xlink'])
            station_path = catalog_ref.get(href_key)
            station_urls.append('{}/{}'.format(
                dir_path,
                parse.urlparse(station_path).path),
            )

        station_urls = station_urls[:10]  # TODO - remove

        # build a list of relevant datasets for each station
        stations = self._station_catalogs(station_urls)
        for station in stations:
            for dataset in station.xpath('//catalog:dataset', namespaces=namespaces):
                if self._is_using_dataset(dataset.get('name')):
                    dataset_paths.append(dataset.get('urlPath'))

        # build a list of processors for all the relevant datasets
        for dataset_path in dataset_paths:
            label, _ = os.path.splitext(os.path.basename(dataset_path))  # remove extension since it's handled later
            url = '{}://{}/{}/{}'.format(
                self._provider_url_parsed.scheme,
                self._provider_url_parsed.hostname,
                'thredds/dodsC',
                dataset_path,
            )
            processors_data.append(ProcessorData(
                named_storm_id=self._named_storm.id,
                provider_id=self._provider.id,
                url=url,
                label=label,
            ))

        return processors_data

    def _station_catalogs(self, station_urls) -> List[etree.ElementTree]:
        """
        Fetches the station urls in parallel via tasks.
        :param station_urls: list of station catalog urls
        :return: list of lxml station elements
        """
        task_group = celery.group([tasks.fetch_url.s(url, self._verify_ssl) for url in station_urls])
        task_promise = task_group()
        stations = task_promise.get()
        stations = [etree.parse(BytesIO(s.encode())) for s in stations]
        return stations

    def _is_using_dataset(self, dataset: str) -> bool:
        """
        Determines if we're using this dataset.
        Format: "20cm4h9999.nc" for real-time and "20cm4h2018.nc" for specific year
        """
        # build a map of years to datasets
        matched = self.RE_PATTERN.match(dataset)
        if matched:
            year = int(matched.group('year'))
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)

            # determine if the start/end dates are within the REALTIME days
            within_realtime_start = (self._named_storm_covered_data.date_start + timedelta(days=self.REALTIME_DAYS)) >= now
            within_realtime_end = (self._named_storm_covered_data.date_end + timedelta(days=self.REALTIME_DAYS)) >= now

            # "real-time" dataset
            if year == self.REALTIME_YEAR:
                return any([within_realtime_start, within_realtime_end])
            # historical dataset
            else:
                # we'll never need the "historical" dataset if the whole date range is within the REALTIME days
                need_both = within_realtime_start and within_realtime_end
                return not need_both and year in [self._named_storm_covered_data.date_start.year, self._named_storm_covered_data.date_end.year]
        return False
