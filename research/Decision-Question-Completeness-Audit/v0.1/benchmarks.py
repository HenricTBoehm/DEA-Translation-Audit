"""Public NIST coefficient acceptance benchmarks; synthetic omissions are explicit."""

from fractions import Fraction
from hashlib import sha256
from math import fsum, sqrt
from pathlib import Path
import re
from time import perf_counter_ns

DATA = Path(__file__).with_name("data")
TOLERANCE = Fraction(1, 100_000_000)
CASES = {
    "Norris": ((0, 1), 0, 36, "intercept_enabled"),
    "Pontius": ((0, 1, 2), 2, 40, "quadratic_enabled"),
}


def parse(blob):
    before, data = blob.decode("ascii").split("Data:       y", 1)
    pairs = [tuple(map(Fraction, line.split())) for line in data.splitlines()[1:] if line.strip()]
    cert = {int(i): Fraction(bit) for i, bit in re.findall(r"^\s+B(\d+)\s+(\S+)\s+\S+\s*$", before, re.M)}
    formula = next(line.strip() for line in before.splitlines() if line.lstrip().startswith("y ="))
    return pairs, cert, formula


def exact_fit(pairs, degrees):
    """Solve the rational normal equations by elimination."""
    table = [[sum(x ** (left + right) for y, x in pairs) for right in degrees]
             + [sum(x ** left * y for y, x in pairs)] for left in degrees]
    for i in range(len(table)):
        j = next(j for j in range(i, len(table)) if table[j][i])
        table[i], table[j] = table[j], table[i]
        pivot = table[i][i]
        table[i] = [a / pivot for a in table[i]]
        for j, row in enumerate(table):
            if j != i:
                table[j] = [a - row[i] * b for a, b in zip(row, table[i])]
    return {power: row[-1] for power, row in zip(degrees, table)}


def qr_fit(pairs, degrees):
    """Independent scaled modified Gram-Schmidt solve on the design columns."""
    xmax = float(max(abs(x) for _, x in pairs))
    y = [float(y) for y, _ in pairs]
    q, upper = [], [[0.0 for _ in degrees] for _ in degrees]

    def dot(a, b):
        return fsum(x * y for x, y in zip(a, b))

    for j, power in enumerate(degrees):
        column = [(float(x) / xmax) ** power for _, x in pairs]
        for i, unit in enumerate(q):
            upper[i][j] = dot(unit, column)
            column = [v - upper[i][j] * u for v, u in zip(column, unit)]
        upper[j][j] = sqrt(dot(column, column))
        q.append([v / upper[j][j] for v in column])
    result = [0.0 for _ in degrees]
    for i in reversed(range(len(degrees))):
        result[i] = (dot(q[i], y) - fsum(upper[i][j] * result[j]
                     for j in range(i + 1, len(degrees)))) / upper[i][i]
    return {power: c / xmax ** power for power, c in zip(degrees, result)}


def max_rel(coefficients, certified):
    return max(abs(coefficients.get(k, 0) - gold) / abs(gold) for k, gold in certified.items())


def evaluate():
    reports, times = {}, {}
    for name, (powers, omitted, expected_n, dimension) in CASES.items():
        start = perf_counter_ns()
        source = (DATA / f"{name}.dat").read_bytes()
        pairs, certified, formula = parse(source)
        if (len(pairs) != expected_n or set(certified) != set(powers)
                or tuple(map(int, re.findall(r"B(\d+)", formula))) != powers):
            raise AssertionError((name, len(pairs), certified))
        read = perf_counter_ns()
        runs = {}
        for label, terms in (("published_terms", powers), ("term_omitted", tuple(k for k in powers if k != omitted))):
            first, second = exact_fit(pairs, terms), qr_fit(pairs, terms)
            error = max_rel(first, certified)
            error_qr = max_rel(second, certified)
            label_exact, label_qr = ("ACCEPT" if error <= TOLERANCE else "REJECT",
                                     "ACCEPT" if error_qr <= float(TOLERANCE) else "REJECT")
            if label_exact != label_qr:
                raise AssertionError((name, label, error, error_qr))
            runs[label] = {"terms": list(terms), "exact_coefficients_as_decimal": {str(k): format(float(v), ".16g") for k, v in first.items()},
                           "qr_coefficients_as_decimal": {str(k): format(v, ".16g") for k, v in second.items()},
                           "max_relative_error_exact": format(float(error), ".9g"),
                           "max_relative_error_qr": format(error_qr, ".9g"), "decision": label_exact}
        if (runs["published_terms"]["decision"], runs["term_omitted"]["decision"]) != ("ACCEPT", "REJECT"):
            raise AssertionError(runs)
        checked = perf_counter_ns()
        reports[name] = {"observations": len(pairs), "required_terms": list(powers), "documented_formula": formula, "injected_omission": omitted,
                         "parameter": dimension, "source_sha256": sha256(source).hexdigest(),
                         "certified_coefficients": {str(k): str(c) for k, c in certified.items()},
                         "tolerance": str(TOLERANCE), "runs": runs}
        times[name] = {"read_parse_and_check_ms": (read - start) / 1e6,
                       "fit_checks_and_witness_construction_ms": (checked - read) / 1e6}
    return reports, times
