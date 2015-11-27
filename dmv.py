from bs4 import BeautifulSoup
from collections import namedtuple
from contextlib import suppress
from datetime import datetime
import logging
import requests


logger = logging.getLogger(__name__)


DMV_BY_ID = {
    537: 'ALTURAS',
    587: 'ARLETA',
    661: 'ARVIN',
    570: 'AUBURN',
    529: 'BAKERSFIELD',
    679: 'BAKERSFIELD SW',
    641: 'BANNING',
    582: 'BARSTOW',
    576: 'BELL GARDENS',
    606: 'BELLFLOWER',
    585: 'BISHOP',
    528: 'BLYTHE',
    597: 'BRAWLEY',
    550: 'CAPITOLA',
    625: 'CARMICHAEL',
    520: 'CHICO',
    613: 'CHULA VISTA',
    580: 'CLOVIS',
    603: 'COALINGA',
    564: 'COLUSA',
    581: 'COMPTON',
    523: 'CONCORD',
    534: 'CORTE MADERA',
    628: 'COSTA MESA',
    524: 'CRESCENT CITY',
    514: 'CULVER CITY',
    599: 'DALY CITY',
    598: 'DAVIS',
    615: 'DELANO',
    669: 'EL CAJON',
    527: 'EL CENTRO',
    556: 'EL CERRITO',
    685: 'EL MONTE',
    526: 'EUREKA',
    621: 'FAIRFIELD',
    643: 'FALL RIVER MILLS',
    655: 'FOLSOM',
    657: 'FONTANA',
    590: 'FORT BRAGG',
    644: 'FREMONT',
    505: 'FRESNO',
    646: 'FRESNO NORTH',
    607: 'FULLERTON',
    627: 'GARBERVILLE',
    623: 'GILROY',
    510: 'GLENDALE',
    670: 'GOLETA',
    541: 'GRASS VALLEY',
    565: 'HANFORD',
    609: 'HAWTHORNE',
    579: 'HAYWARD',
    635: 'HEMET',
    546: 'HOLLISTER',
    508: 'HOLLYWOOD',
    652: 'HOLLYWOOD WEST',
    578: 'INDIO',
    610: 'INGLEWOOD',
    521: 'JACKSON',
    647: 'KING CITY',
    605: 'LAGUNA HILLS',
    687: 'LAKE ISABELLA',
    530: 'LAKEPORT',
    595: 'LANCASTER',
    617: 'LINCOLN PARK',
    622: 'LODI',
    589: 'LOMPOC',
    692: 'LOMPOC DLPC',
    507: 'LONG BEACH',
    502: 'LOS ANGELES',
    693: 'LOS ANGELES DLPC',
    650: 'LOS BANOS',
    640: 'LOS GATOS',
    533: 'MADERA',
    658: 'MANTECA',
    566: 'MARIPOSA',
    536: 'MERCED',
    557: 'MODESTO',
    511: 'MONTEBELLO',
    639: 'MOUNT SHASTA',
    540: 'NAPA',
    584: 'NEEDLES',
    662: 'NEWHALL',
    586: 'NORCO',
    686: 'NOVATO',
    504: 'OAKLAND CLAREMONT',
    604: 'OAKLAND COLISEUM',
    596: 'OCEANSIDE',
    522: 'OROVILLE',
    636: 'OXNARD',
    683: 'PALM DESERT',
    659: 'PALM SPRINGS',
    690: 'PALMDALE',
    601: 'PARADISE',
    509: 'PASADENA',
    574: 'PASO ROBLES',
    634: 'PETALUMA',
    592: 'PITTSBURG',
    525: 'PLACERVILLE',
    631: 'PLEASANTON',
    532: 'POMONA',
    573: 'PORTERVILLE',
    676: 'POWAY',
    544: 'QUINCY',
    612: 'RANCHO CUCAMONGA',
    558: 'RED BLUFF',
    551: 'REDDING',
    626: 'REDLANDS',
    548: 'REDWOOD CITY',
    633: 'REEDLEY',
    577: 'RIDGECREST',
    545: 'RIVERSIDE',
    656: 'RIVERSIDE EAST',
    673: 'ROCKLIN',
    543: 'ROSEVILLE',
    501: 'SACRAMENTO',
    602: 'SACRAMENTO SOUTH',
    539: 'SALINAS',
    568: 'SAN ANDREAS',
    512: 'SAN BERNARDINO',
    648: 'SAN CLEMENTE',
    506: 'SAN DIEGO',
    519: 'SAN DIEGO CLAIREMONT',
    503: 'SAN FRANCISCO',
    516: 'SAN JOSE',
    645: 'SAN JOSE DLPC',
    547: 'SAN LUIS OBISPO',
    620: 'SAN MARCOS DESCANSO',
    689: 'SAN MARCOS RANCHEROS',
    593: 'SAN MATEO',
    619: 'SAN PEDRO',
    677: 'SAN YSIDRO',
    542: 'SANTA ANA',
    549: 'SANTA BARBARA',
    632: 'SANTA CLARA',
    563: 'SANTA MARIA',
    616: 'SANTA MONICA',
    630: 'SANTA PAULA',
    555: 'SANTA ROSA',
    668: 'SANTA TERESA',
    567: 'SEASIDE',
    660: 'SHAFTER',
    680: 'SIMI VALLEY',
    569: 'SONORA',
    538: 'SOUTH LAKE TAHOE',
    698: 'STANTON DLPC',
    517: 'STOCKTON',
    531: 'SUSANVILLE',
    575: 'TAFT',
    672: 'TEMECULA',
    663: 'THOUSAND OAKS',
    608: 'TORRANCE',
    642: 'TRACY',
    513: 'TRUCKEE',
    594: 'TULARE',
    553: 'TULELAKE',
    649: 'TURLOCK',
    638: 'TWENTYNINE PALMS',
    535: 'UKIAH',
    588: 'VACAVILLE',
    554: 'VALLEJO',
    515: 'VAN NUYS',
    560: 'VENTURA',
    629: 'VICTORVILLE',
    559: 'VISALIA',
    624: 'WALNUT CREEK',
    583: 'WATSONVILLE',
    572: 'WEAVERVILLE',
    618: 'WEST COVINA',
    611: 'WESTMINSTER',
    591: 'WHITTIER',
    571: 'WILLOWS',
    637: 'WINNETKA',
    561: 'WOODLAND',
    552: 'YREKA',
    562: 'YUBA CITY',
}

BEHIND_THE_WHEEL_URL = 'https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do'

# Example: 'Thursday, December 31, 2015 at 9:00 AM'
TIME_FORMAT = '%A, %B %d, %Y at %I:%M %p'

Result = namedtuple('Result', ['date', 'dmv'])


def get_dmv_response(data):
    return requests.post(BEHIND_THE_WHEEL_URL, data=data)


def get_dmv_date_raw(response):
    soup = BeautifulSoup(response, 'html.parser')
    try:
        return soup.select('.alert')[1].text
    except IndexError:
        logger.debug(soup.select('.alert'))
        raise FetchingError


def convert_date_raw(raw_date):
    return datetime.strptime(raw_date, TIME_FORMAT)


def get_dmv_date(data):
    response = get_dmv_response(data)
    date_raw = get_dmv_date_raw(response.content)
    return convert_date_raw(date_raw)


def behind_the_wheel_dates(data, clear_cache=False):
    return repository.behind_the_wheel_dates(data, clear_cache)


def print_behind_the_wheel_dates(data, clear_cache=False):
    return repository.print_behind_the_wheel_dates(data, clear_cache)


class FetchingError(Exception):
    pass


class DMV:
    def __init__(self, id, city):
        self.id = id
        self.city = city

    def behind_the_wheel_date(self, data):
        """
        Get the first behind the wheel date.
        """
        payload = data.copy()
        payload.update({
            "officeId": self.id,
            "numberItems": "1",
            "requestedTask": "DT",
            "resetCheckFields": "true",
        })
        return get_dmv_date(payload)


class DMVRepository:
    def __init__(self, dmv_by_id):
        self.dmv_by_id = dmv_by_id
        self.dmv_by_city = {
            city: id
            for id, city in dmv_by_id.items()
        }
        self.dates = []

    def get_dmv(self, id):
        return DMV(id, self.dmv_by_id[id])

    def get_by_city(self, city):
        city = city.upper()
        return DMV(self.dmv_by_city[city], city)

    def fetch_dates(self, data):
        for dmv in self:
            with suppress(FetchingError):
                self.dates.append(Result(dmv.behind_the_wheel_date(data), dmv))

    def behind_the_wheel_dates(self, data, clear_cache=False):
        if clear_cache or not self.dates:
            self.dates = []
            self.fetch_dates(data)
        return sorted(self.dates, key=lambda result: result.date)

    def print_behind_the_wheel_dates(self, data, clear_cache=False):
        for result in behind_the_wheel_dates(data, clear_cache):
            print(result.dmv.city, result.date)

    def __iter__(self):
        for id in self.dmv_by_id:
            yield self.get_dmv(id)


repository = DMVRepository(DMV_BY_ID)
