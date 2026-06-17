"""Tests unitaires preprocessing — Sprint 2 / S8."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.preprocessing import PumpPreprocessor, build_encoder, load_and_preprocess


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "amount_tsh": [100.0, 0.0, 50.0],
            "date_recorded": ["2013-01-01", "2012-06-15", "2014-03-20"],
            "funder": ["Government", "Unknown Funder XYZ", "Government"],
            "gps_height": [100, -5, 200],
            "installer": ["DWE", "other installer", "DWE"],
            "longitude": [0.0, 35.0, 36.0],
            "latitude": [-2.0, -4.0, -3.0],
            "num_private": [0, 0, 1],
            "basin": ["Lake Victoria", "Lake Victoria", "Rufiji"],
            "region": ["Mara", "Mara", "Iringa"],
            "public_meeting": ["True", "False", None],
            "permit": ["True", "False", "False"],
            "construction_year": [0, 2005, 2010],
            "extraction_type": ["gravity", "submersible", "handpump"],
            "management": ["vwc", "wug", "vwc"],
            "payment": ["pay annually", "never pay", "pay monthly"],
            "water_quality": ["soft", "soft", "milky"],
            "source_type": ["spring", "borehole", "borehole"],
            "quantity_group": ["enough", "enough", "enough"],
            "extraction_type_group": ["gravity", "submersible", "handpump"],
            "quality_group": ["good", "good", "good"],
            "region_code": [1, 1, 2],
            "district_code": [10, 10, 20],
            "recorded_by": ["GeoData Institute Ltd"] * 3,
            "scheme_name": ["", "", ""],
            "wpt_name": ["a", "b", "c"],
            "subvillage": ["sv1", "sv2", "sv3"],
            "ward": ["w1", "w2", "w3"],
            "lga": ["l1", "l2", "l3"],
        }
    )


@pytest.fixture
def fitted_prep(sample_df) -> PumpPreprocessor:
    prep = PumpPreprocessor(reference_year=2014, top_n=1)
    prep.fit(sample_df)
    return prep


def test_gps_zero_replaced(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[0, "longitude"] != 0.0
    assert result.loc[0, "latitude"] != 0.0


def test_year_unknown_flag(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[0, "year_unknown"] == 1
    assert result.loc[1, "year_unknown"] == 0
    assert result.loc[0, "construction_year"] > 0


def test_gps_height_negative_imputed(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert (result["gps_height"] >= 0).all()


def test_tsh_zero_flag_and_imputation(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[1, "tsh_is_zero"] == 1
    assert result.loc[1, "amount_tsh"] > 0


def test_funder_installer_top_n_grouped(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[0, "funder"] == "government"
    assert result.loc[1, "funder"] == "other"


def test_pump_age_created(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert "pump_age" in result.columns
    assert result.loc[1, "pump_age"] == 2014 - 2005


def test_temporal_features(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[0, "year_recorded"] == 2013
    assert result.loc[0, "month_recorded"] == 1
    assert result.loc[0, "day_of_year"] == 1


def test_age_at_recording(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert result.loc[1, "age_at_recording"] == 2012 - 2005


def test_dist_to_basin_center(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert "dist_to_basin_center" in result.columns
    assert (result["dist_to_basin_center"] >= 0).all()


def test_redundant_columns_dropped(fitted_prep, sample_df):
    result = fitted_prep.transform(sample_df)
    assert "quantity_group" not in result.columns
    assert "extraction_type_group" not in result.columns


def test_transform_requires_fit(sample_df):
    prep = PumpPreprocessor()
    with pytest.raises(RuntimeError):
        prep.transform(sample_df)


def test_build_encoder_returns_transformer():
    encoder = build_encoder(scaler="standard")
    assert encoder is not None


def test_load_and_preprocess_integration():
    train, test = load_and_preprocess(save=False)
    assert train.shape[0] == 59400
    assert "status_group" in train.columns
    assert test.shape[0] == 14850
    feature_cols = PumpPreprocessor().get_feature_columns()
    present = [c for c in feature_cols if c in train.columns]
    assert train[present].isna().sum().sum() == 0
