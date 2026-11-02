import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from HOF import HOF_Hanover


def test_v2_terminus_line_has_no_empty_first_column():
    hof = HOF_Hanover()
    hof.add_terminus(eric="101", destination="Central")

    terminus_line = hof.show_hof_v2().split("[addterminus_list]\n", 1)[1].split("\n", 1)[0]

    assert not terminus_line.startswith("\t")
    assert terminus_line.split("\t", 1)[0] == "101"


def test_v2_round_trip_preserves_fares_and_multi_digit_ddu_sections(tmp_path):
    hof = HOF_Hanover()
    hof.add_stopreporter(
        name="Central",
        EngDisplay="Central",
        ChiSeconds=1,
        EngSeconds=2,
        Outbound_sectionfare=12.0,
        Inbound_sectionfare=13.5,
    )
    hof.add_ddu(
        RTNO="101",
        Outbound_dir="Central",
        Inbound_dir="Harbour",
        Outbound_price=12.0,
        Inbound_price=13.5,
        sectiontimes_Y=24,
        sectiontimes_Z=12,
    )
    filename = tmp_path / "roundtrip.hof"
    hof.export_hof_v2(str(filename))

    loaded = HOF_Hanover()
    loaded.load_from_hof(str(filename))

    assert loaded.stopreporter[0].Outbound_sectionfare == 12.0
    assert loaded.stopreporter[0].Inbound_sectionfare == 13.5
    assert loaded.ddu[0].sectiontimes_Y == 24
    assert loaded.ddu[0].sectiontimes_Z == 12


def test_v1_busstop_list_declares_exact_stop_count():
    busstop_list = HOF_Hanover.Infosystem.busstop_list(["Central"], "101")

    assert "[infosystem_busstop_list]\n1\n101\nCentral" in str(busstop_list)


def test_v1_stopreporter_round_trip_preserves_directional_fares(tmp_path):
    hof = HOF_Hanover()
    hof.add_stopreporter(
        name="Central",
        EngDisplay="Central",
        ChiSeconds=1,
        EngSeconds=2,
        Outbound_sectionfare=12.0,
        Inbound_sectionfare=13.5,
    )
    filename = tmp_path / "roundtrip-v1.hof"
    hof.export_hof(str(filename))

    loaded = HOF_Hanover()
    loaded.load_from_hof(str(filename))

    assert loaded.stopreporter[0].Outbound_sectionfare == 12.0
    assert loaded.stopreporter[0].Inbound_sectionfare == 13.5
