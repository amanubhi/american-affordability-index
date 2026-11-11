import pytest
from refresh_kaggle import reconcile


def old():
    return [dict(series_id='APU0000X', date='2026-07-01', year='2026', month='7',
                 item='Example', category='Food', unit='lb', price='2')]


def incoming(date='2026-07-01', price='2'):
    return dict(series_id='APU0000X', date=date, price_usd=price,
                area_code='0000', seasonally_adjusted='False')


def test_extends_without_inventing_missing_prices():
    rows, metrics = reconcile(old(), [incoming(), incoming('2026-08-01', ''), incoming('2026-09-01', '3')])
    assert len(rows) == 2
    assert metrics['added_rows'] == 1
    assert rows[-1]['unit'] == 'lb'
    assert rows[-1]['month'] == '9'


def test_rejects_history_revisions():
    with pytest.raises(ValueError, match='historical prices changed'):
        reconcile(old(), [incoming(price='4')])


def test_rejects_lost_history():
    with pytest.raises(ValueError, match='omits'):
        reconcile(old(), [incoming('2026-09-01')])


def test_rejects_duplicate_keys():
    with pytest.raises(ValueError, match='Duplicate'):
        reconcile(old(), [incoming(), incoming()])
