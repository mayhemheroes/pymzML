#!/usr/bin/env python3
"""Behavioral oracle (known-answer test) for pymzML.

Exercises the SAME parsing pipeline the fuzzer drives — pymzml.run.Reader over an mzML file ->
spectrum index -> decoded m/z peak array — and ASSERTS specific decoded values against a known
input shipped in the upstream tree (tests/data/example.mzML). A no-op / neutered program (which
prints nothing) FAILS test.sh, because the SELFTEST_PASS marker and its asserted values are only
printed when every assertion holds.

Runs fully offline: the OBO ontology files pymzml needs are bundled in the package (pymzml/obo).
"""
import os

import pymzml.run as run

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)  # /mayhem
MZML = os.path.join(SRC, "tests", "data", "example.mzML")

# 1) Parse a known mzML file and assert run-level metadata.
reader = run.Reader(MZML)
mzml_version = reader.info["mzml_version"]
spectrum_count = reader.info["spectrum_count"]
assert mzml_version == "1.1.0", mzml_version
assert spectrum_count == 2918, spectrum_count

# 2) Index into a known spectrum and assert decoded peak data.
spec = reader[1]
assert spec.ID == 1, spec.ID
assert spec.ms_level == 1, spec.ms_level
npeaks = len(spec.mz)
assert npeaks == 917, npeaks
mz0 = round(float(spec.mz[0]), 4)
assert mz0 == 70.0658, mz0

# 3) Reject clearly malformed input — a non-mzML byte stream must not parse as a spectrum stream.
import tempfile

with tempfile.NamedTemporaryFile("w+b", suffix=".mzML") as tf:
    tf.write(b"this is definitely not an mzML document\n")
    tf.flush()
    rejected = False
    try:
        bad = run.Reader(tf.name)
        _ = bad[1]  # force parsing of the (absent) first spectrum
    except Exception:
        rejected = True
    assert rejected, "BUG: malformed input was accepted by pymzml.run.Reader"

print(
    "SELFTEST_PASS mzml_version=%s spectrum_count=%d ms_level=%d npeaks=%d"
    % (mzml_version, spectrum_count, spec.ms_level, npeaks)
)
