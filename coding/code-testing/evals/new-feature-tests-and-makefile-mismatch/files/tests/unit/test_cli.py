from tally import cli, core


def test_record_via_cli_persists_and_totals_reports_it(capsys):
    assert cli.main(["record", "pushups", "--count", "12"]) == 0
    assert cli.main(["totals"]) == 0
    out = capsys.readouterr().out
    assert "pushups\t12" in out
    assert core.totals() == {"pushups": 12}
