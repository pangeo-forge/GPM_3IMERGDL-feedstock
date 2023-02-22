import xarray


def test_doi(zarr_store: xarray.Dataset):
    """
    Verify the DOI attribute is set correctly
    """
    assert zarr_store.attrs["DOI"] == "10.5067/GPM/IMERGDL/DAY/06"


def test_coverage(zarr_store: xarray.Dataset):
    """
    Verify that we have all the lats & lons
    """
    assert len(zarr_store.lat) == 1800
    assert len(zarr_store.lon) == 3600


def test_variables(zarr_store: xarray.Dataset):
    """
    Verify that the variables we care about are in here
    """
    expected_vars = ['HQprecipitation', 'HQprecipitation_cnt', 'HQprecipitation_cnt_cond', 'lat', 'lon', 'precipitationCal', 'precipitationCal_cnt', 'precipitationCal_cnt_cond', 'randomError', 'randomError_cnt', 'time', 'time_bnds']
    for var in expected_vars:
        assert var in list(zar_store.variables)
    
