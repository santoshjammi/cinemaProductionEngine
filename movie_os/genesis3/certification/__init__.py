"""GENESIS 3 — Production Certification.

Implements the ProductionReadiness certificate issuing workflow:
1. `certify()` compiles QA Department results into a ``ProductionCertificate``.
2. ``format_certificate()`` renders that certificate as a beautifully
   formatted text block (boxes, status indicators, scores).

Exports::
    CertificationEngine
    CertificationRequest
    ProductionCertificate
"""

from __future__ import annotations

from movie_os.genesis3.certification.models import (  # noqa: F401
    CertificationRequest,
    ProductionCertificate,
)
from movie_os.genesis3.certification.engine import CertificationEngine  # noqa: F401
