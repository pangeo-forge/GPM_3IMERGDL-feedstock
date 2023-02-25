"""
A recipe to move GPM_#IMERGDL from <DC> to a cloud analysis ready format.
"""

import apache_beam as beam
from pangeo_forge_cmr import files_from_cmr
from pangeo_forge_earthdatalogin import OpenURLWithEarthDataLogin
from pangeo_forge_recipes.transforms import OpenWithXarray, StoreToZarr

files = files_from_cmr(
    shortname='GPM_3IMERGDL',
    concat_dim="time",
    nitems_per_file=1
)

recipe = (
    beam.Create(files.items())
    | OpenURLWithEarthDataLogin()
    | OpenWithXarray()
    | StoreToZarr(
        store_name='gpm-3imergdl',
        target_chunks={'time': 2},
        combine_dims=files.combine_dim_keys,
    )
)

