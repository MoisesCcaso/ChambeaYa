from abc import ABC
from profiles.domain.i_intern_repository import IInternRepository
from profiles.domain.i_company_repository import ICompanyRepository


class IProfileRepository(IInternRepository, ICompanyRepository, ABC):
    """Combined profile interface kept for compatibility with aggregated contracts (SOLID-ISP)."""
    pass

