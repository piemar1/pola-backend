from parameterized import parameterized
from test_plus import TestCase

from pola import logic_produkty_w_sieci
from pola.gpc.factories import GPCBrickFactory
from pola.integrations.produkty_w_sieci import ProductQueryResult
from pola.logic_produkty_w_sieci import create_from_api, is_code_supported
from pola.product.models import Product
from pola.report.models import Report

TEST_PRODUCT_NAME = "Probiotyk intymny"

TEST_EAN13 = "5900084231145"
TEST_NIP = "7792308851"


class TestIsCodeSupported(TestCase):
    @parameterized.expand(
        [
            (TEST_EAN13, True),
            (
                "777" + TEST_EAN13[3:],
                False,
            ),
            (TEST_EAN13[0:-3], False),
        ]
    )
    def test_should_check_code(self, code, result):
        self.assertEqual(is_code_supported(code), result)


class TestCreateFromApi(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        super().setUp()

    def test_should_create_product_brand_and_company_when_product_is_missing(self):
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "brand": "4Her",
                    "company": {
                        "name": "company-name",
                        "nip": TEST_NIP,
                        "street": "company-street",
                        "webPage": "company-page",
                        "city": "company-city",
                        "postalCode": "company-postal-code",
                    },
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13,
                get_products_response=ProductQueryResult.parse_obj(product_query_response),
                product=None,
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertEqual(product_db.brand.name, product_query_response["results"][0]['brand'])
        self.assertEqual(product_db.company.name, product_query_response["results"][0]['company']['name'])
        self.assertEqual(Report.objects.count(), 0)
        self.maxDiff = None
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=company-name, nip=7792308851. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about brand: '
                'name=4Her. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product missing. Creating a new product.',
            ],
        )

    def test_should_set_gpc_when_gpc_in_product_is_not_set(self):
        code = '5900102025473'

        product_query_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "facets": {},
            "results": [
                {
                    "id": "e4aa0425-f552-4a59-91c3-c5932cb1e327",
                    "gtinNumber": f"0{code}",
                    "gtinStatus": "active",
                    "name": "Gorzka 70% cocoa 90g - czekolada pełna",
                    "targetMarket": ["WW"],
                    "netContent": "90.0g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "isPublic": True,
                    "isVerified": False,
                    "lastModified": "2021-04-20T13:24:24.970000+00:00",
                    "brand": "Wawel",
                    "company": {
                        "name": "WAWEL Spółka Akcyjna",
                        "nip": "6760076868",
                        "street": "ul. Władysława Warneńczyka 14",
                        "webPage": "http://www.wawel.com.pl",
                        "city": "Kraków",
                        "postalCode": "30-520",
                    },
                    "gpc": "10000045",
                }
            ],
        }
        gpc_brick = GPCBrickFactory(code="10000045")
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=code,
                get_products_response=ProductQueryResult.parse_obj(product_query_response),
                product=None,
            )
        product_db = Product.objects.get(code=code)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=WAWEL Spółka Akcyjna, nip=6760076868. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about brand: '
                'name=Wawel. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product missing. Creating a new product.',
            ],
        )
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.gpc_brick.code, "10000045")
        self.assertEqual(product_db.gpc_brick.pk, gpc_brick.pk)
        self.assertEqual(Report.objects.count(), 0)

    def test_should_create_product_when_product_is_missing(self):
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13,
                get_products_response=ProductQueryResult.parse_obj(product_query_response),
                product=None,
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertIsNone(product_db.brand)
        self.assertIsNone(product_db.company)
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about company.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about brand.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product missing. Creating a new product.',
            ],
        )

    def test_should_create_product_and_company_when_product_is_missing(self):
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "company": {
                        "name": "company-name",
                        "nip": TEST_NIP,
                        "street": "company-street",
                        "webPage": "company-page",
                        "city": "company-city",
                        "postalCode": "company-postal-code",
                    },
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13,
                get_products_response=ProductQueryResult.parse_obj(product_query_response),
                product=None,
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertIsNone(product_db.brand)
        self.assertEqual(product_db.company.name, product_query_response["results"][0]['company']['name'])
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=company-name, nip=7792308851. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about brand.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product missing. Creating a new product.',
            ],
        )

    def test_should_create_product_and_brand_when_product_is_missing(self):
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "brand": "4Her",
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13,
                get_products_response=ProductQueryResult.parse_obj(product_query_response),
                product=None,
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertEqual(product_db.brand.name, product_query_response["results"][0]['brand'])
        self.assertIsNone(product_db.company)
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about company.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'brand: name=4Her. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product missing. Creating a new product.',
            ],
        )

    def test_should_create_brand_and_company_when_product_exists_and_company_and_brand_is_missing_in_db(self):
        p = Product.objects.create(
            name=TEST_PRODUCT_NAME,
            code=TEST_EAN13,
            commit_desc="Utworzono produkt przez test",
        )
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "brand": "4Her",
                    "company": {
                        "name": "company-name",
                        "nip": TEST_NIP,
                        "street": "company-street",
                        "webPage": "company-page",
                        "city": "company-city",
                        "postalCode": "company-postal-code",
                    },
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13, get_products_response=ProductQueryResult.parse_obj(product_query_response), product=p
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertEqual(product_db.brand.name, product_query_response["results"][0]['brand'])
        self.assertEqual(product_db.company.name, product_query_response["results"][0]['company']['name'])
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=company-name, nip=7792308851. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'brand: name=4Her. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product exists. Updating a product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown company was '
                'found. Updating the product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown brand was '
                'found. Updating the product.',
            ],
        )

    def test_should_do_nothing_when_product_exists(self):
        p = Product.objects.create(
            name=TEST_PRODUCT_NAME,
            code=TEST_EAN13,
            commit_desc="Utworzono produkt przez test",
        )
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13, get_products_response=ProductQueryResult.parse_obj(product_query_response), product=p
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertIsNone(product_db.brand)
        self.assertIsNone(product_db.company)
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about company.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about brand.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product exists. Updating a product.',
            ],
        )

    def test_should_set_company_when_product_without_company_exists(self):
        p = Product.objects.create(
            name=TEST_PRODUCT_NAME,
            code=TEST_EAN13,
            commit_desc="Utworzono produkt przez test",
        )

        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "company": {
                        "name": "company-name",
                        "nip": TEST_NIP,
                        "street": "company-street",
                        "webPage": "company-page",
                        "city": "company-city",
                        "postalCode": "company-postal-code",
                    },
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13, get_products_response=ProductQueryResult.parse_obj(product_query_response), product=p
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertIsNone(product_db.brand)
        self.assertEqual(product_db.company.name, product_query_response["results"][0]['company']['name'])
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=company-name, nip=7792308851. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about brand.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product exists. Updating a product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown company was '
                'found. Updating the product.',
            ],
        )

    def test_should_set_gpc_when_product_without_gpc_exists(self):
        p = Product.objects.create(
            name=TEST_PRODUCT_NAME,
            code=TEST_EAN13,
            commit_desc="Utworzono produkt przez test",
        )

        product_query_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "facets": {},
            "results": [
                {
                    "id": "e4aa0425-f552-4a59-91c3-c5932cb1e327",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "gtinStatus": "active",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["WW"],
                    "netContent": "90.0g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "isPublic": True,
                    "isVerified": False,
                    "lastModified": "2021-04-20T13:24:24.970000+00:00",
                    "brand": "Wawel",
                    "company": {
                        "name": "WAWEL Spółka Akcyjna",
                        "nip": "6760076868",
                        "street": "ul. Władysława Warneńczyka 14",
                        "webPage": "http://www.wawel.com.pl",
                        "city": "Kraków",
                        "postalCode": "30-520",
                    },
                    "gpc": "10000045",
                }
            ],
        }
        gpc_brick = GPCBrickFactory(code="10000045")
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13, get_products_response=ProductQueryResult.parse_obj(product_query_response), product=p
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertEqual(product_db.gpc_brick.code, gpc_brick.code)
        self.assertEqual(product_db.gpc_brick.pk, gpc_brick.pk)

        self.assertEqual(product_db.company.name, product_query_response["results"][0]['company']['name'])
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'company: name=WAWEL Spółka Akcyjna, nip=6760076868. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Company created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'brand: name=Wawel. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product exists. Updating a product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown company was '
                'found. Updating the product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown brand was '
                'found. Updating the product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown GPC Brick name '
                'was found. Updating the product.',
            ],
        )

    def test_should_create_product_and_brand_when_product_exists(self):
        p = Product.objects.create(
            name=TEST_PRODUCT_NAME,
            code=TEST_EAN13,
            commit_desc="Utworzono produkt przez test",
        )
        product_query_response = {
            "count": 1,
            "next": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=2000",
            "prev": "<baseURL>/external_api/v1/products/?last_modified__gte=2020-06-01&limit=1000?offset=0",
            "results": [
                {
                    "id": "a7b5528c-5ba3-4090-a1ae-14bfd704a736",
                    "gtinNumber": f"0{TEST_EAN13}",
                    "name": TEST_PRODUCT_NAME,
                    "targetMarket": ["PL"],
                    "netVolume": 30,
                    "unit": "g",
                    "imageUrls": [],
                    "description": None,
                    "descriptionLanguage": "pl",
                    "productPage": None,
                    "productCardPage": None,
                    "isPublic": True,
                    "lastModified": "2020-06-01T14:03:41.722000+00:00",
                    "brand": "4Her",
                    "gpc": "",
                }
            ],
        }
        with self.assertLogs(level='INFO', logger=logic_produkty_w_sieci.LOGGER) as log:
            result_product = create_from_api(
                code=TEST_EAN13, get_products_response=ProductQueryResult.parse_obj(product_query_response), product=p
            )
        product_db = Product.objects.get(code=TEST_EAN13)
        self.assertEqual(result_product.pk, product_db.pk)
        self.assertEqual(product_db.name, product_query_response["results"][0]['name'])
        self.assertEqual(product_db.brand.name, product_query_response["results"][0]['brand'])
        self.assertIsNone(product_db.company)
        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(
            log.output,
            [
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result miss information about company.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Result contains information about '
                'brand: name=4Her. Checking db.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Brand created: True',
                'INFO:/app/pola/logic_produkty_w_sieci.py:Product exists. Updating a product.',
                'INFO:/app/pola/logic_produkty_w_sieci.py:A previously unknown brand was '
                'found. Updating the product.',
            ],
        )
