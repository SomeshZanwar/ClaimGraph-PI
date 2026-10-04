from decimal import Decimal

import pytest

from app.ingestion.cms_carrier import CarrierRowError, parse_carrier_row


def base_row() -> dict[str, str]:
    return {
        "DESYNPUF_ID": "BENE001",
        "CLM_ID": "CLAIM001",
        "CLM_FROM_DT": "20090101",
        "CLM_THRU_DT": "20090103",
        "ICD9_DGNS_CD_1": "25000",
        "PRF_PHYSN_NPI_1": "9990001111",
        "TAX_NUM_1": "TAX001",
        "HCPCS_CD_1": "99213",
        "LINE_NCH_PMT_AMT_1": "80.25",
        "LINE_BENE_PTB_DDCTBL_AMT_1": "10.00",
        "LINE_BENE_PRMRY_PYR_PD_AMT_1": "0",
        "LINE_COINSRNC_AMT_1": "16.05",
        "LINE_ALOWD_CHRG_AMT_1": "106.30",
        "LINE_PRCSG_IND_CD_1": "A",
        "LINE_ICD9_DGNS_CD_1": "25000",
    }


def test_parse_carrier_row_extracts_claim_and_line() -> None:
    parsed = parse_carrier_row(base_row())

    assert parsed.beneficiary_id == "BENE001"
    assert parsed.claim_id == "CLAIM001"
    assert parsed.claim_from_date.isoformat() == "2009-01-01"
    assert parsed.diagnosis_codes == ["25000"]
    assert len(parsed.lines) == 1
    assert parsed.lines[0].hcpcs_code == "99213"
    assert parsed.lines[0].allowed_charge_amount == Decimal("106.30")


def test_parse_carrier_row_rejects_missing_claim_id() -> None:
    row = base_row()
    row["CLM_ID"] = ""

    with pytest.raises(CarrierRowError) as exc_info:
        parse_carrier_row(row)

    assert exc_info.value.code == "MISSING_CLAIM_ID"


def test_parse_carrier_row_rejects_invalid_date_range() -> None:
    row = base_row()
    row["CLM_FROM_DT"] = "20090104"
    row["CLM_THRU_DT"] = "20090103"

    with pytest.raises(CarrierRowError) as exc_info:
        parse_carrier_row(row)

    assert exc_info.value.code == "INVALID_DATE_RANGE"


def test_parse_carrier_row_rejects_invalid_money() -> None:
    row = base_row()
    row["LINE_NCH_PMT_AMT_1"] = "not-money"

    with pytest.raises(CarrierRowError) as exc_info:
        parse_carrier_row(row)

    assert exc_info.value.code == "INVALID_DECIMAL"
