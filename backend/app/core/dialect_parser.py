"""
HelvetiaVeritas - Deterministic Cantonal Dialect Parser
======================================================
Heuristic and phonological classifier for Swiss German Alemannic dialects:
- ZH: Züritüütsch (Canton Zurich)
- BE: Bärndütsch (Canton Bern)
- BS: Baseldytsch (Canton Basel-Stadt)
- SG: Sanggallerdütsch (Canton St. Gallen / Ostschweiz)
- CH-DE: Überregionales Schweizerdeutsch (General Alemannic)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from app.config import settings
from app.schemas.audit_schema import (
    CantonalDialectResult,
    LexicalMarkerMatch,
    PhonologyRuleMatch,
)

logger = logging.getLogger("helvetia_veritas.dialect_parser")


class NonAlemannicLanguageError(ValueError):
    """Raised when submitted text is identified as foreign or non-Alemannic."""
    pass


class CantonalDialectParser:
    """Deterministic, rule-grounded dialect parser for Swiss Alemannic varieties."""

    # Foreign language guardrails
    FOREIGN_PATTERNS = {
        "Französisch": re.compile(
            r"\b(je|tu|il|elle|nous|vous|ils|le|la|les|mon|ma|mes|notre|votre|pour|avec|dans|sur|est|sont|qui|que|bonjour|merci|monsieur|madame|tribunal|demande)\b",
            re.IGNORECASE
        ),
        "Italienisch": re.compile(
            r"\b(io|tu|lui|lei|noi|voi|loro|il|lo|la|i|gli|le|mio|mia|nostro|per|con|in|su|tra|fra|sono|siamo|che|chi|buongiorno|grazie|signore|signora)\b",
            re.IGNORECASE
        ),
        "Englisch": re.compile(
            r"\b(the|is|are|was|were|have|has|had|this|that|these|those|with|for|from|they|them|their|what|when|where|which|please|hello|dear|landlord|tenant)\b",
            re.IGNORECASE
        ),
        "Spanisch": re.compile(
            r"\b(el|la|los|las|un|una|unos|unas|yo|tu|el|ella|nosotros|vosotros|ellos|por|para|con|en|sobre|gracias|hola|senor|senora|muy|mas|pero|demanda)\b",
            re.IGNORECASE
        ),
        "Portugiesisch": re.compile(
            r"\b(eu|tu|ele|ela|nos|vos|eles|elas|o|a|os|as|um|uma|uns|umas|meu|minha|por|para|com|em|sobre|obrigado|obrigada|ola|senhor|senhora|muito|mais)\b",
            re.IGNORECASE
        )
    }

    def __init__(self, markers_path: Optional[Path] = None):
        self.markers_path = markers_path or settings.CANTONAL_MARKERS_PATH
        self.corpus_data: Dict = {}
        self.compiled_phonology_rules: Dict[str, List[Tuple[str, re.Pattern, str, float]]] = {}
        self.lexical_lookup: Dict[str, List[Tuple[str, str, float]]] = {}
        self._load_corpus()

    def _load_corpus(self) -> None:
        """Load and index cantonal markers, n-grams, and regex phonology rules."""
        if not self.markers_path.exists():
            logger.error("Cantonal markers file not found at %s", self.markers_path)
            raise FileNotFoundError(f"Markers file missing: {self.markers_path}")

        with open(self.markers_path, "r", encoding="utf-8") as f:
            self.corpus_data = json.load(f)

        cantons = self.corpus_data.get("cantons", {})
        for canton_code, canton_info in cantons.items():
            # Compile regex phonology rules
            rules_list = []
            for rule in canton_info.get("phonology_rules", []):
                try:
                    pattern = re.compile(rule["pattern"], re.IGNORECASE)
                    rules_list.append((
                        rule["name"],
                        pattern,
                        rule["description"],
                        float(rule["weight"])
                    ))
                except re.error as e:
                    logger.warning("Failed to compile rule %s: %s", rule.get("name"), e)
            self.compiled_phonology_rules[canton_code] = rules_list

            # Index lexical markers (support multi-word tokens)
            for marker in canton_info.get("markers", []):
                tok = marker["token"].lower().strip()
                if tok not in self.lexical_lookup:
                    self.lexical_lookup[tok] = []
                self.lexical_lookup[tok].append((
                    canton_code,
                    marker.get("gloss_de", ""),
                    float(marker.get("weight", 1.0))
                ))

        logger.info(
            "Loaded Cantonal markers: %d lexical tokens, %d phonology rules across %d cantons",
            len(self.lexical_lookup),
            sum(len(v) for v in self.compiled_phonology_rules.values()),
            len(cantons)
        )

    def _check_language_guardrail(self, text: str) -> None:
        """Verifies that the text is not an unsupported non-Alemannic language."""
        for lang_name, pattern in self.FOREIGN_PATTERNS.items():
            foreign_matches = pattern.findall(text)
            if len(foreign_matches) >= 3:
                raise NonAlemannicLanguageError(
                    f"Der eingegebene Text wurde als {lang_name} identifiziert ({len(foreign_matches)} Fremdsprachenmarker). "
                    "HelvetiaVeritas verarbeitet ausschliesslich Schweizerdeutsche Mundarten (Züritüütsch, Bärndütsch, Baseldytsch, Sanggallerdütsch usw.)."
                )

    def parse(self, text: str, canton_hint: Optional[str] = None) -> CantonalDialectResult:
        """
        Analyze raw Swiss German text, extract cantonal lexical & phonological
        markers, and compute classification confidence.
        """
        cleaned_text = text.strip()
        self._check_language_guardrail(cleaned_text)

        lower_text = cleaned_text.lower()
        words = re.findall(r"\b[\wÄÖÜäöüéèà']+\b", lower_text)
        word_count = len(words) or 1

        canton_scores: Dict[str, float] = {code: 0.0 for code in self.corpus_data.get("cantons", {})}
        matched_markers: List[LexicalMarkerMatch] = []
        matched_phonology: List[PhonologyRuleMatch] = []
        seen_markers = set()

        # 1. Multi-word lexical search (n-grams in full text)
        for token, matches in self.lexical_lookup.items():
            if " " in token:
                if token in lower_text:
                    for canton_code, gloss, weight in matches:
                        canton_scores[canton_code] += weight * 1.5
                        marker_key = f"{token}_{canton_code}"
                        if marker_key not in seen_markers:
                            seen_markers.add(marker_key)
                            matched_markers.append(LexicalMarkerMatch(
                                token=token,
                                gloss_de=gloss,
                                weight=weight,
                                canton=canton_code
                            ))

        # 2. Single-word lexical search (with proclitic stripping e.g. d'wöschchuchi -> wöschchuchi)
        for w in words:
            # Strip proclitic clitics: d', s', m', z'
            clean_w = re.sub(r"^[dsmz]['’]", "", w)
            for candidate in (w, clean_w):
                if candidate in self.lexical_lookup:
                    for canton_code, gloss, weight in self.lexical_lookup[candidate]:
                        canton_scores[canton_code] += weight
                        marker_key = f"{candidate}_{canton_code}"
                        if marker_key not in seen_markers:
                            seen_markers.add(marker_key)
                            matched_markers.append(LexicalMarkerMatch(
                                token=candidate,
                                gloss_de=gloss,
                                weight=weight,
                                canton=canton_code
                            ))
                    break

        # 3. Phonology & Morphological Regex evaluation
        for canton_code, rules in self.compiled_phonology_rules.items():
            for rule_name, pattern, description, weight in rules:
                matches = pattern.findall(lower_text)
                if matches:
                    match_samples = []
                    for m in matches:
                        sample_str = m[0] if isinstance(m, tuple) else m
                        if sample_str and sample_str not in match_samples:
                            match_samples.append(sample_str)
                    
                    sample_summary = ", ".join(match_samples[:4])
                    rule_score = weight * min(len(matches), 3)
                    canton_scores[canton_code] += rule_score

                    matched_phonology.append(PhonologyRuleMatch(
                        rule_name=rule_name,
                        description=description,
                        matched_sample=sample_summary,
                        weight=round(rule_score, 2)
                    ))

        # 4. Apply optional user/administrative canton hint prior
        if canton_hint and canton_hint.upper() in canton_scores:
            hint_upper = canton_hint.upper()
            canton_scores[hint_upper] += 2.5

        # 5. Calculate distribution & top canton
        total_score = sum(canton_scores.values())
        distribution: Dict[str, float] = {}

        if total_score > 0:
            for c_code, score in canton_scores.items():
                distribution[c_code] = round(score / total_score, 4)
            top_canton = max(canton_scores.items(), key=lambda x: x[1])[0]
            sorted_scores = sorted(canton_scores.values(), reverse=True)
            top_s = sorted_scores[0]
            runner_s = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
            margin = (top_s - runner_s) / max(top_s, 1.0)
            confidence = min(0.99, max(0.55, 0.5 + (margin * 0.45)))
            canton_info = self.corpus_data.get("cantons", {}).get(top_canton, {})
            canton_name = canton_info.get("name", f"Kanton {top_canton}")
            dialect_name = canton_info.get("dialect_name", "Schweizerdeutsch")
            coat_of_arms = canton_info.get("coat_of_arms", "🇨🇭")
            color = canton_info.get("color", "#D8232A")
        else:
            # Neutral Pan-Swiss fallback rather than false Zurich assumption
            for c_code in canton_scores:
                distribution[c_code] = round(1.0 / len(canton_scores), 4)
            top_canton = "CH-DE"
            confidence = 0.50
            canton_name = "Überkantonal / Allgemein"
            dialect_name = "Schweizerdeutsche Mundart (Allgemein)"
            coat_of_arms = "🇨🇭"
            color = "#D8232A"

        dialect_density = round(len(matched_markers) / max(word_count, 1), 3)

        return CantonalDialectResult(
            canton_code=top_canton,
            canton_name=canton_name,
            dialect_name=dialect_name,
            confidence=round(confidence, 2),
            coat_of_arms=coat_of_arms,
            cantonal_color=color,
            detected_markers=matched_markers,
            phonology_matches=matched_phonology,
            distribution=distribution,
            dialect_density=dialect_density,
            word_count=word_count
        )


# Singleton instance
dialect_parser = CantonalDialectParser()
