from scripts.lib.ids import valid_curated_id,valid_staging_id
def test_ids():
    assert valid_curated_id('atlas-comp.fake.service','atlas-comp')
    assert not valid_curated_id('atlas-flow.fake.service','atlas-comp')
    assert valid_staging_id('STG-20260807-fake-service')
