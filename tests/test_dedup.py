import pandas as pd

from mining_intel.processing.dedup import build_projects, normalize_project_key, split_provinces


def test_normalize_project_key_is_case_and_accent_insensitive():
    assert normalize_project_key("Los Azules") == normalize_project_key("Los azules")
    assert normalize_project_key("Salar del Rincón") == normalize_project_key("salar del rincon")
    assert normalize_project_key("  Veladero  ") == normalize_project_key("veladero")


def test_normalize_project_key_blank_name_returns_none():
    assert normalize_project_key("") is None
    assert normalize_project_key("   ") is None
    assert normalize_project_key(None) is None


def test_split_provinces_splits_combined_values():
    assert split_provinces("Salta/ Catamarca") == ["Salta", "Catamarca"]
    assert split_provinces("San Juan/ Catamarca") == ["San Juan", "Catamarca"]
    assert split_provinces("Salta") == ["Salta"]


def _announcement(**overrides) -> dict:
    base = {
        "external_id": "1",
        "name": "Veladero",
        "company": "Barrick Gold",
        "province": "San Juan",
        "mineral": "Oro",
        "stage": "Ampliación",
        "investment_usd": 100.0,
        "announced_date": "01/20 2020",
    }
    base.update(overrides)
    return base


def test_multiple_announcements_with_different_company_spellings_merge_into_one_project():
    df = pd.DataFrame(
        [
            _announcement(external_id="1", company="Barrick Gold", investment_usd=225_000_000, announced_date="03/20 2020"),
            _announcement(external_id="2", company="Barrick Gold - Shandong Gold", investment_usd=628_000_000, announced_date="10/20 2020"),
            _announcement(external_id="3", company="Barrick Gold-Shandong Gold", investment_usd=120_000_000, announced_date="12/21 2021"),
        ]
    )

    projects_df, provinces_df, external_id_to_key = build_projects(df)

    assert len(projects_df) == 1
    project = projects_df.iloc[0]
    assert project["name"] == "Veladero"
    assert project["announcement_count"] == 3
    assert project["total_investment_usd"] == 225_000_000 + 628_000_000 + 120_000_000
    assert len(set(external_id_to_key.values())) == 1
    assert provinces_df["province"].tolist() == ["San Juan"]


def test_blank_name_announcements_never_merge_with_each_other():
    df = pd.DataFrame(
        [
            _announcement(external_id="1", name="", company="Kobrea Exploration", province="Mendoza", mineral="Cobre"),
            _announcement(external_id="2", name="", company="Khanij Bidesh India -Kabil-", province="Catamarca", mineral="Litio"),
        ]
    )

    projects_df, _, external_id_to_key = build_projects(df)

    assert len(projects_df) == 2
    assert external_id_to_key["1"] != external_id_to_key["2"]


def test_multi_province_project_stays_one_project_but_counts_both_provinces():
    df = pd.DataFrame(
        [
            _announcement(external_id="1", name="Sal de Oro", company="POSCO", province="Salta", investment_usd=831_000_000),
            _announcement(external_id="2", name="Sal de Oro", company="POSCO", province="Salta/ Catamarca", investment_usd=800_000_000),
        ]
    )

    projects_df, provinces_df, _ = build_projects(df)

    assert len(projects_df) == 1
    assert projects_df.iloc[0]["announcement_count"] == 2
    assert projects_df.iloc[0]["total_investment_usd"] == 831_000_000 + 800_000_000

    provinces = set(provinces_df["province"])
    assert provinces == {"Salta", "Catamarca"}
    assert "Salta/ Catamarca" not in provinces
