"""
A recipe to move GPM_#IMERGDL from <DC> to a cloud analysis ready format.
"""

import apache_beam as beam
from pangeo_forge_cmr import get_cmr_granule_links
from pangeo_forge_earthdatalogin import OpenURLWithEarthDataLogin
from pangeo_forge_recipes.patterns import pattern_from_file_sequence
from pangeo_forge_recipes.transforms import (OpenURLWithFSSpec, OpenWithXarray,
                                             StoreToZarr)

shortname = 'GPM_3IMERGDL'

all_files = get_cmr_granule_links(shortname)

pattern = pattern_from_file_sequence(
    all_files,
    concat_dim="time",
    nitems_per_file=1,
)

recipe = (
    beam.Create(pattern.items())
    | OpenURLWithEarthDataLogin()
    | OpenWithXarray()
    | StoreToZarr(
        store_name='gpm-3imergdl',
        target_chunks={'time': 1},
        combine_dims=pattern.combine_dim_keys,
    )
)

