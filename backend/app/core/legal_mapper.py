"""
HelvetiaVeritas - Statutory Matcher and Swiss Code Cross-Referencer
===================================================================
Maps normalized citizen grievances and administrative petitions against
Swiss statutory provisions: ZGB (Civil Code), OR (Code of Obligations),
and SchKG (Debt Collection and Bankruptcy Act).
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.schemas.audit_schema import (
    LegalAnalysisResult,
    MatchedLegalArticle,
)

logger = logging.getLogger("helvetia_veritas.legal_mapper")


class SwissLegalMapper:
    """Statutory matcher cross-referencing text against the Swiss Codes Index."""

    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path or settings.SWISS_CODES_INDEX_PATH
        self.articles_corpus: List[Dict] = []
        self._load_corpus()

    def _load_corpus(self) -> None:
        """Load and index Swiss federal statutes."""
        if not self.index_path.exists():
            logger.error("Swiss codes index file not found at %s", self.index_path)
            raise FileNotFoundError(f"Codes index missing: {self.index_path}")

        with open(self.index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.articles_corpus = data.get("articles", [])

        logger.info("Loaded %d Swiss statutory articles for legal alignment", len(self.articles_corpus))

    def map_statutes(
        self,
        normalized_text: str,
        raw_text: str = "",
        canton_code: str = "ZH",
        domain_hint: Optional[str] = None
    ) -> LegalAnalysisResult:
        """
        Cross-reference normalized text and raw claim against Swiss civil,
        tenancy, labor, and municipal codes.
        """
        combined_text = f"{normalized_text} {raw_text}".lower()
        matched_articles: List[MatchedLegalArticle] = []
        domain_tallies: Dict[str, float] = {}

        for art in self.articles_corpus:
            art_id = art["article_id"]
            law = art["law"]
            art_num = art["article_number"]
            title = art["title_de"]
            domain = art["domain"]
            keywords = art.get("keywords", [])
            summary = art.get("summary_de", "")
            remedy = art.get("remedy_action_de", "")
            authority = art.get("competent_authority", "")
            fedlex_url = art.get("fedlex_url", "")

            matched_kws = []
            score = 0.0

            # 1. Match explicit keywords
            for kw in keywords:
                pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                matches = len(re.findall(pattern, combined_text))
                if matches > 0:
                    matched_kws.append(kw)
                    score += 0.25 * min(matches, 3)

            # 2. Check title / domain tokens
            title_tokens = [t.lower() for t in re.findall(r"\b\w{4,}\b", title)]
            for tt in title_tokens:
                if tt in combined_text:
                    score += 0.15

            # 3. Domain hint bonus
            if domain_hint and domain_hint.lower() in domain.lower():
                score += 0.35

            # If score above threshold or high keyword density
            if score > 0.15:
                # Normalize score to max 0.98
                relevance = min(0.98, max(0.52, score / 1.5))
                matched_articles.append(MatchedLegalArticle(
                    article_id=art_id,
                    law=law,
                    article_number=art_num,
                    title_de=title,
                    domain=domain,
                    relevance_score=round(relevance, 2),
                    summary_de=summary,
                    remedy_action_de=remedy,
                    competent_authority=authority,
                    fedlex_url=fedlex_url,
                    matched_keywords=matched_kws
                ))
                domain_tallies[domain] = domain_tallies.get(domain, 0.0) + score

        # Sort articles by relevance descending
        matched_articles.sort(key=lambda a: a.relevance_score, reverse=True)
        top_articles = matched_articles[:5]

        # Triage fallback if no statutory provision met the relevance threshold
        if not top_articles:
            fallback_article = MatchedLegalArticle(
                article_id="CH-RECHTSAUSKUNFT",
                law="ZPO / Anwaltsgesetz",
                article_number="Art. 117 ZPO",
                title_de="Unentgeltliche Rechtsberatung & Schlichtung",
                domain="Allgemeines Schweizerisches Verwaltungs- & Zivilrecht",
                relevance_score=0.55,
                summary_de="Das Anliegen konnte keinem spezifischen Spezialartikel zugeordnet werden. Es greift die allgemeine kantonale Rechtsauskunft und das Schlichtungswesen.",
                remedy_action_de="Wenden Sie sich an die unentgeltliche Rechtsauskunft des kantonalen Anwaltsverbandes oder die lokale Gemeindekanzlei für eine Ersteinschätzung.",
                competent_authority="Kantonales Friedensrichteramt / Bezirksgericht",
                fedlex_url="https://www.fedlex.admin.ch/eli/cc/2010/262/de#art_117",
                matched_keywords=["allgemeine_rechtsberatung"]
            )
            top_articles = [fallback_article]

        # Determine primary domain
        if domain_tallies:
            primary_domain = max(domain_tallies.items(), key=lambda x: x[1])[0]
        elif top_articles:
            primary_domain = top_articles[0].domain
        else:
            primary_domain = "Schweizerisches Zivil- und Verwaltungsrecht (Allgemein)"

        # Generate procedural steps and authorities
        procedural_steps = self._derive_procedural_steps(top_articles, canton_code)
        authorities = self._derive_authorities(top_articles, canton_code)

        return LegalAnalysisResult(
            primary_domain=primary_domain,
            matched_articles=top_articles,
            recommended_procedural_steps=procedural_steps,
            competent_authorities=authorities
        )

    def _derive_procedural_steps(
        self,
        articles: List[MatchedLegalArticle],
        canton_code: str
    ) -> List[str]:
        """Derives actionable procedural advice based on matched articles."""
        steps = []
        art_ids = {a.article_id for a in articles}

        if "OR-259a" in art_ids or "OR-259d" in art_ids:
            steps.append(
                "1. Schriftliche Mängelrüge per Einschreiben (A-Post Plus oder Einschreiben) an die Liegenschaftsverwaltung mit Fristansetzung zur Behebung (z. B. 10 bis 14 Tage) zustellen."
            )
            steps.append(
                "2. Mietzinsreduktion gemäss Art. 259d OR rückwirkend ab Meldedatum geltend machen."
            )
        if "OR-259g" in art_ids:
            steps.append(
                "3. Bei fruchtlosem Ablauf der Behebungsfrist die Hinterlegung künftiger Mietzinse bei der zuständigen Schlichtungsbehörde schriftlich ankündigen und vollziehen."
            )
        if "ZGB-684" in art_ids or "PBG-BAU" in art_ids:
            steps.append(
                "1. Lückenloses Immissionsprotokoll (Datum, Uhrzeit, Dezibel-Schätzung, Zeugen) führen gemäss Art. 8 ZGB."
            )
            steps.append(
                "2. Formelle Einsprache gegen das Baugesuch / Unterlassungsaufforderung innert der kantonalen Auflagefrist einreichen."
            )
        if "OR-322" in art_ids or "OR-328" in art_ids:
            steps.append(
                "1. Detaillierte tabellarische Überstundenaufstellung und Lohnabrechnungskopie zusammenstellen."
            )
            steps.append(
                "2. Formelle Mahnung mit 10-tägiger Zahlungsfrist unter Androhung der Einleitung rechtlicher Schritte beim Arbeitsgericht zustellen."
            )
        if "SchKG-74" in art_ids:
            steps.append(
                "1. Sofort innert 10 Tagen nach Erhalt des Zahlungsbefehls Rechtsvorschlag beim Betreibungsamt erheben (keine Begründung erforderlich)."
            )
        if "SchKG-82" in art_ids:
            steps.append(
                "1. Vorliegen einer qualifizierten schriftlichen Schuldanerkennung (z. B. Darlehensvertrag) verifizieren."
            )
            steps.append(
                "2. Gesuch um provisorische Rechtsöffnung beim zuständigen Rechtsöffnungsrichter des Betreibungsortes einreichen."
            )
        if "DBG-132" in art_ids:
            steps.append(
                "1. Fristgerechte schriftliche Einsprache innert der verwirkbaren 30-Tage-Frist beim kantonalen Steueramt einreichen."
            )
            steps.append(
                "2. Korrigierte Belege, Lohnausweise und Begründung der Steuerabzüge fristwahrend nachreichen."
            )
        if "KVG-64" in art_ids:
            steps.append(
                "1. Schriftliches Gesuch um Erlass einer anfechtbaren Verfügung gemäss Art. 49 ATSG bei der Krankenkasse verlangen."
            )
            steps.append(
                "2. Antrag auf individuelle Prämienverbilligung (IPV) bei der kantonalen Ausgleichskasse stellen."
            )

        # Baseline fallback steps if empty
        if not steps:
            steps.append(
                "1. Schriftliche Eingabe per Einschreiben mit genauer Sachverhaltsdarstellung an die Gegenpartei zustellen."
            )
            steps.append(
                "2. Relevante Beweismittel (Fotos, Verträge, Quittungen) gemäss Art. 8 ZGB sichern."
            )
            steps.append(
                f"3. Bei Nichteinigung Schlichtungsverfahren bei der zuständigen Behörde im Kanton {canton_code} einleiten."
            )

        return steps

    def _derive_authorities(
        self,
        articles: List[MatchedLegalArticle],
        canton_code: str
    ) -> List[str]:
        """Maps cantonal jurisdiction and competent judicial organs."""
        authorities = set()
        canton_prefixes = {
            "ZH": "Bezirk Zürich / Kanton Zürich",
            "BE": "Kanton Bern / Bern-Mittelland",
            "BS": "Kanton Basel-Stadt",
            "SG": "Kanton St. Gallen / Kreisgericht"
        }
        loc = canton_prefixes.get(canton_code, f"Kanton {canton_code}")

        for a in articles:
            if a.competent_authority:
                authorities.add(f"{a.competent_authority} ({loc})")

        if not authorities:
            authorities.add(f"Zuständige Schlichtungsbehörde / Friedensrichteramt ({loc})")

        return sorted(list(authorities))


# Singleton instance
legal_mapper = SwissLegalMapper()
