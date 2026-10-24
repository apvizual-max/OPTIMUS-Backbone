"""Anti-mimicry detectors A1-A12 + R-2, evaluated mechanically.

The doctrine (03_INTELLIGENCE/filters/ANTI_MIMICRY_DETECTORS.md) documents 13
detectors. The previous implementation exposed 4 of them, all Romanian-only and
all written without diacritics, so they could not fire on English output and
could not reliably fire on correctly spelled Romanian either.

Two constraints shape this module:

1. `code_no_romanian` forbids Romanian diacritics in .py source. So the patterns
   below stay ASCII, and the INPUT is folded instead (see `fold`). That way
   "imi pare rau" matches "imi pare ra u" with diacritics, and an English
   phrase matches its own ASCII spelling. Nothing is lost to the encoding law.

2. A detector that cannot be evaluated from its inputs must report
   NOT_EVALUATED, never PASS. A silent pass is the exact failure this module
   exists to catch, so it must not reproduce one. `coverage` in the result says
   how many detectors actually ran.
"""

import re
import unicodedata
from typing import Any, Dict, List, Tuple

# Detectors that need conversation context this tool is not given.
NEEDS_CONTEXT = {"A1", "A8", "R-2"}

PASS = "PASS"
FAIL = "FAIL"
NOT_EVALUATED = "NOT_EVALUATED"

DOCUMENTED = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "R-2"]


def fold(text: str) -> str:
    """Lowercase and strip diacritics so ASCII patterns match real Romanian.

    The question mark is PRESERVED as ' ? '. Stripping it made every
    interrogative pattern ('ok?', 'procedez?') unfireable, because a check that
    cannot match is worse than no check - it silently reports a clean result.
    """
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text.lower())
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    # Collapse punctuation, but keep '?' because the ban list is built on questions.
    stripped = stripped.replace("?", " ? ")
    return re.sub(r"[^a-z0-9?\s]", " ", stripped)


def _has(text: str, *needles: str) -> List[str]:
    return [n for n in needles if n in text]


def F(*needles: str) -> Tuple[str, ...]:
    """Normalise needles the same way as the input.

    Patterns are written naturally ("i'm an ai", "top-right", "iarta-ma"). If a
    needle keeps its punctuation it can never appear in folded text, because
    fold() replaces punctuation with spaces. An unfireable pattern is worse
    than no pattern: it contributes nothing while implying coverage. Normalising
    both sides here removes that whole class of bug instead of fixing it
    needle by needle.
    """
    return tuple(fold(n) for n in needles)


# Evidence markers: a claim is only supported if the output shows a probe ran.
#
# Split by whether the marker is FALSIFIABLE. A real probe leaves machine-shaped
# residue - an exit code, an HTTP status, a count, a hash, a command echo. None of
# those can be produced by asserting a virtue.
#
# "verified", "confirmed", "measured" and "tested" can: any boast that names its
# own reliability satisfies the check built to catch it. Keeping them in the
# evidence set made A4 unfireable against exactly the output it exists for - a
# self-certified overclaim passed with the detail "completion claim is
# accompanied by evidence", where the only evidence was the word "verified".
# A needle that matches too easily is the mirror of one that cannot match, and it
# is just as useless: both report a verdict instead of measuring anything.
# Evidence must be FALSIFIABLE and REFORMAT-PROOF.
#
# fold() rewrites punctuation to spaces, so any needle whose match could be
# manufactured by reformatting prose is unsafe: "ls -" folds to "ls  ", which is
# exactly what "too**ls** are" folds to. A command name is therefore not evidence -
# bolded or hyphenated prose can invent one. Digits are the discriminator: folding
# cannot synthesise a "0", and every real result carries one. Hence the invariant
# asserted by the suite: every member of _PROOF contains a digit.
_PROOF = F(
    "exit 0", "exit=0", "exit 1", "exit=1", "http 200", "http=200", "http 400",
    "status 200", "0 failed", "sha256", "200 ok",
)
# "passed" on its own is a boast: "All checks passed" is exactly what a hollow
# claim sounds like. Proof is a RESULT, so it must carry a number. Regexes, not
# needles, because a needle cannot express "preceded by digits".
_PROOF_RE = (
    re.compile(r"\d+\s+passed"),
    re.compile(r"\d+\s+failed"),
    re.compile(r"exit\s*[= ]\s*\d"),
    re.compile(r"http\s+\d{3}"),
    re.compile(r"sha\d+"),
)
_SELF_ASSERTION = F(
    "verified", "confirmed", "tested", "measured", "probe", "ran the",
    "output:", "returned", "found:", "test suite",
)
_EVIDENCE = _PROOF + _SELF_ASSERTION
_ABSENCE_EVIDENCE = _EVIDENCE + F("does not exist", "not present", "no such file", "empty result", "not found")
_COMPLETION = F("gata", "complet", "terminat", "finalizat", "done", "finished", "all set", "100%", "fully working",
                "fully functional", "production ready", "production-ready", "everything works", "perfectly working")
_UI_WORDS = F("butonul", "buton", "meniul", "menu", "click pe", "click here",
              "the button", "top right", "top-right", "bottom left", "bottom-left")
_EXTERNAL_BLAME = F(
    "modelul meu", "training-ul", "mea anume", "anthropic", "openai", "default-ul",
    "my training", "my model", "my defaults", "because the model", "the model made me",
    "i was programmed to", "my system prompt", "language model limitations",
    # The AI identity used as a shield instead of taking a position. This is
    # external attribution wearing a first-person hat.
    "as an ai language model", "as an ai assistant", "i am an ai", "i'm an ai",
    "i'm just an ai", "i am just an ai", "as an ai, i",
)
_APOLOGY = F(
    "imi pare rau", "iarta-ma", "scuze", "inteleg frustrarea", "as it goes again",
    "i apologize", "i apologise", "sorry for the confusion", "my apologies",
    "i understand your frustration", "i deeply apologize", "again, i apologize",
)
_PERMISSION_ASK = F(
    "ok?", "procedez?", "sa continuu?", "trec la", "vrei sa", "e bine?",
    "ce zici?", "shall i proceed", "would you like me to", "do you want me to",
    "should i proceed", "let me know if", "wdyt?", "confirm before i",
)
_STORY_ACK = F(
    "interesanta analogie", "frumoasa analogie", "metafor bun", "great analogy",
    "good analogy", "nice metaphor", "what a great point", "i like this analogy",
)
# A completion claim is only supported by a PROOF, never by the claim's own wording.
_MIN_PROOF_SIGNALS = 2


# Two KINDS of result must both be present, and they must be DIFFERENT evidence.
#   COUNT-shaped  : "76 passed", "0 failed"  -> a tally from a run
#   STATUS-shaped : "exit=0", "http 200", "sha256" -> an outcome or an artefact
# A real report carries both. A boast carries one, repeated.
_COUNT_RE = (
    re.compile(r"\d+\s+passed"),
    re.compile(r"\d+\s+failed"),
)
_STATUS_RE = (
    re.compile(r"exit\s*[= ]\s*\d"),
    re.compile(r"http\s+\d{3}"),
    re.compile(r"sha\d+"),
)


def _distinct_kinds(text: str) -> set:
    """Which KINDS of result appear, counting each distinct form once.

    Counting spans is not enough: a boast that says "0 failed, 0 failed" contains
    two spans but only one piece of evidence. Nor is counting instances enough,
    because a pasted results line - "as the vendor claims: 128 passed, 0 failed" -
    is a quotation, not a run. Counting distinct FORMS across both kinds means the
    text has to offer a tally AND an outcome that differ from each other.
    """
    kinds = set()
    for rx in _COUNT_RE:
        for m in rx.finditer(text):
            kinds.add(('count', re.sub(r'\s+', ' ', m.group(0)).strip()))
    for rx in _STATUS_RE:
        for m in rx.finditer(text):
            kinds.add(('status', re.sub(r'\s+', ' ', m.group(0)).strip()))
    return kinds


def _proof_kinds(text: str) -> set:
    """The distinct result forms present, for reporting."""
    return {form for _kind, form in _distinct_kinds(text)}


def _has_proof(text: str) -> bool:
    """True when the text carries at least two DISTINCT result forms.

    A single result-shaped token is no better than a single word: digits are legal
    in ordinary prose, so "All green: 0 failed. Complete.", "Left via exit 0
    door" and "I used sha256 as required" all name a proof marker without
    measuring anything.

    Counting SPANS is not enough - "0 failed, 0 failed" is two spans but one piece
    of evidence, and it defeats the gate. So the unit counted is the distinct
    result FORM: "76 passed" and "0 failed" are two forms, "0 failed" twice is one.
    A real report offers several; a boast repeats one.

    CEILING, stated plainly because it cannot be fixed in text: this matcher
    cannot distinguish a MEASUREMENT from a QUOTATION. "As the vendor claims:
    128 passed, 0 failed" satisfies this rule and is still unverified. The rule
    removes the cheap forgeries; it does not make a claim true. Only a caller
    that can attest `tools_called` closes that gap - which is why the result
    echoes the raw flag next to this verdict rather than hiding it.
    """
    return len(_distinct_kinds(text)) >= _MIN_PROOF_SIGNALS


def _compact(value: str) -> str:
    """Letters and digits only - no separators left to exploit."""
    return re.sub(r"[^a-z0-9]+", "", value)


def _completion_hits(text: str) -> list:
    """Completion markers present, matched on either key.

    fold() maps hyphens to spaces, so "com-plete" folded to "com plete", matched no
    completion marker, and A4 passed VACUOUSLY - it found no completion claim at
    all rather than accepting one. Falling back to a separator-free key removes
    the whole class of separator-injection evasion.
    """
    hits = [n for n in _COMPLETION if _has(text, n)]
    if hits:
        # "production ready" and "production-ready" fold to the same string; report
        # the marker once instead of naming it twice in the detail.
        return sorted(set(hits), key=lambda n: (_compact(text).find(_compact(n)), n))
    key = _compact(text)
    return sorted({n for n in _COMPLETION if _compact(n) in key},
                  key=lambda n: (key.find(_compact(n)), n))


def as_bool(value: Any) -> bool:
    """Read a flag that may arrive as a JSON boolean or as a string.

    `bool("false")` is True. A transport that stringifies a falsy boolean would
    therefore invert every evidence-dependent verdict: the tool would assert that
    a probe ran when the caller explicitly said none did. That is forged evidence,
    which is precisely what A4 and A6 exist to reject.

    Real booleans first, then unambiguous strings, then False for anything
    unrecognised - never a silent default that contradicts the caller.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('true', '1', 'yes', 'y')
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def evaluate(output: str, context: str = "", tools_called: bool = False) -> Dict[str, Any]:
    """Run every documented detector. Returns per-detector verdicts + coverage."""
    tools_called = as_bool(tools_called)
    text = fold(output)
    ctx = fold(context)
    both = text + " " + ctx
    results: List[Dict[str, Any]] = []

    def add(det: str, verdict: str, detail: str = "") -> None:
        results.append({"detector": det, "verdict": verdict, "detail": detail})

    # A1 - answer a "why" with mechanism instead of benefit. Needs the question.
    add("A1", NOT_EVALUATED, "needs the triggering question; output alone cannot decide mechanism vs benefit")

    # A2 - "one thing" must be exactly one imperative.
    if _has(text, "1 lucru", "un singur lucru", "one thing", "1 pas", "one step"):
        imperatives = re.findall(r"(?:^|\n)\s*(?:\d+[.)]\s*)?(?:-|\*)?\s*(run|open|click|select|choose|set|type|press|navigate|install)\b", text)
        if len(imperatives) > 1:
            add("A2", FAIL, "claims one thing but lists %d imperatives" % len(imperatives))
        else:
            add("A2", PASS)
    else:
        add("A2", PASS, "no single-imperative claim present")

    # A3 - a path should be its own line, not buried in a sentence.
    path_in_sentence = re.search(r"[a-z]:[\\/][^\s,;)]+", output) and not re.search(
        r"(?:^|\n)\s*[a-z]:[\\/][^\s]+", output, re.IGNORECASE
    )
    add("A3", FAIL if path_in_sentence else PASS,
        "path embedded in prose instead of its own line" if path_in_sentence else "")

    # A4 - "done" only after a real test.
    completion_hits = _completion_hits(both)
    has_evidence = _has_proof(both) or tools_called
    if completion_hits and not has_evidence:
        add("A4", FAIL, "claims completion (%s) with no test, measurement or tool call" % ", ".join(completion_hits))
    elif completion_hits:
        # A PASS here means "the claim carries result-shaped evidence", NOT "the
        # evidence is real". Text cannot tell a measurement from a quotation, so the
        # verdict says which forms it accepted rather than implying verification.
        add("A4", PASS, "completion claim carries result-shaped evidence (%s); "
                        "this establishes CONSISTENCY WITH a run, not that a run happened"
                        % ", ".join(sorted(_proof_kinds(both))))
    else:
        add("A4", PASS, "no completion claim present")

    # A5 - JSON/config asserted valid must show a parser run.
    shows_json = ("{" in output and "}" in output) or _has(text, "json", "config", "yaml", "manifest")
    if shows_json:
        has_evidence = _has_proof(both) or tools_called
        add("A5", FAIL if not has_evidence else PASS,
            "config/json shown with no parser or validation evidence" if not has_evidence else "")

    # A6 - a claim that something is missing must show the probe that proved it.
    absence_claims = _has(text, "lipseste", "nu exista", "nu merge", "nu este instalat", "not installed",
                          "does not exist", "is missing", "isn't there", "no such", "not present", "absent")
    if absence_claims:
        proven = bool(_has(both, *_ABSENCE_EVIDENCE)) or tools_called
        add("A6", FAIL if not proven else PASS,
            "claims an absence/defect without showing the probe that checked" if not proven else "")

    # A7 - never ask permission instead of deciding.
    hits = _has(both, *_PERMISSION_ASK)
    add("A7", FAIL if hits else PASS,
        "permission-seeking language: %s" % ", ".join(hits) if hits else "")

    # A8 - proactive completeness. Needs the domain history.
    add("A8", NOT_EVALUATED, "needs the domain's known-bug history; not derivable from this text")

    # A9 - frustration becomes an action, not an apology.
    apol = _has(text, *_APOLOGY)
    add("A9", FAIL if apol else PASS,
        "apology instead of action: %s" % ", ".join(apol) if apol else "")

    # A10 - no blame pushed onto an external entity.
    blame = _has(both, *_EXTERNAL_BLAME)
    add("A10", FAIL if blame else PASS,
        "external blame: %s" % ", ".join(blame) if blame else "")

    # A11 - do not describe a UI you have not seen.
    ui = _has(text, *_UI_WORDS)
    saw_ui = bool(_has(text, "screenshot", "screen shot", "i see", "am vazut", "din captura", "in the screenshot")) or tools_called
    if ui and not saw_ui:
        add("A11", FAIL, "describes UI without any evidence of having seen it")
    else:
        add("A11", PASS)

    # A12 - a story must yield an applied rule, not an acknowledgement.
    ack = _has(both, *_STORY_ACK)
    applied = bool(_has(both, "aplicare", "applied", "i will apply", "regula", "rule:", "so i will"))
    if ack and not applied:
        add("A12", FAIL, "acknowledges the analogy but extracts no applied rule")
    else:
        add("A12", PASS)

    # R-2 - a factual claim needs a tool call first.
    if tools_called:
        add("R-2", PASS, "caller reports a tool call backing this output")
    else:
        add("R-2", NOT_EVALUATED, "caller did not report a tool call; cannot confirm empirical verification")

    failures = [r for r in results if r["verdict"] == FAIL]
    evaluated = [r for r in results if r["verdict"] in (PASS, FAIL)]
    not_evaluated = [r for r in results if r["verdict"] == NOT_EVALUATED]

    return {
        "mimicry_detected": bool(failures),
        "detectors_documented": len(DOCUMENTED),
        "detectors_evaluated": len(evaluated),
        "detectors_not_evaluated": len(not_evaluated),
        "not_evaluated_ids": [r["detector"] for r in not_evaluated],
        "coverage_complete": not not_evaluated,
        "score": round(100 * (len(evaluated) - len(failures)) / len(evaluated)) if evaluated else 0,
        "score_meaning": "share of EVALUATED detectors that passed. Not a percentage of the documented set; see coverage_complete.",
        "failures": failures,
        "results": results,
        "scope": "Text-level only. A PASS means no pattern matched, not that the output is truthful.",
        "known_ceiling": (
            "A4 cannot distinguish a measurement from a QUOTATION. Text containing "
            "'128 passed, 0 failed' satisfies it whether or not anything ran, and no "
            "text matcher can close that gap. Treat an A4 PASS as consistency with a "
            "run, not as verification. Only a caller that can attest tools_called "
            "converts it into an actual observation."
        ),
        "caller_must": "pass tools_called when a tool actually ran, and context when the detector needs the triggering question.",
    }