"""Data loading, schemas, catalogs, and normalization."""

from competeiq.data.catalogs import COMPANY_X_CATALOG, COMPANY_Y_CATALOG, DEFAULT_CATALOGS
from competeiq.data.loader import load_all_catalogs, load_catalog_file
from competeiq.data.processor import TracedProductCatalogProcessor
from competeiq.data.schemas import CatalogDict, NormalizedProduct, ProductDict

__all__ = [
    "COMPANY_X_CATALOG",
    "COMPANY_Y_CATALOG",
    "DEFAULT_CATALOGS",
    "TracedProductCatalogProcessor",
    "load_all_catalogs",
    "load_catalog_file",
    "CatalogDict",
    "NormalizedProduct",
    "ProductDict",
]
