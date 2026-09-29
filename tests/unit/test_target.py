from __future__ import annotations

import pandas as pd
import pytest

from aletheia.contracts import SchemaError
from aletheia.data.target import add_adverse_target, map_adverse_target


def test_complete_target_truth_table(dataset_contract) -> None:
    raw = pd.Series([0, 1], name="kredit", dtype="int64")

    mapped = map_adverse_target(raw, dataset_contract)

    assert mapped.tolist() == [1, 0]


def test_target_mapping_preserves_raw_column(dataset_contract) -> None:
    frame = pd.DataFrame({"kredit": [0, 1]})

    mapped = add_adverse_target(frame, dataset_contract)

    assert mapped["kredit"].tolist() == [0, 1]
    assert mapped["adverse_event"].tolist() == [1, 0]


def test_unknown_raw_target_is_rejected(dataset_contract) -> None:
    raw = pd.Series([0, 2], name="kredit")

    with pytest.raises(SchemaError, match="invalid raw target value 2"):
        map_adverse_target(raw, dataset_contract)
