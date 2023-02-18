"""
A recipe to move GPM_#IMERGDL from <DC> to a cloud analysis ready format.
"""
import netrc
import os
from functools import partial

import aiohttp
import apache_beam as beam
from pangeo_forge_cmr import get_cmr_granule_links

from pangeo_forge_recipes import patterns
from pangeo_forge_recipes.patterns import pattern_from_file_sequence
from pangeo_forge_recipes.transforms import OpenURLWithFSSpec, OpenWithXarray, StoreToZarr


# We need to provide EarthData credentials to fetch the files.
# The credentials of the currently logged in user are used, and passed on to the cloud
# as well when the operation is scaled out. This shall be automated with a machine identity
# in the future.
# go here to set up .netrc file: https://disc.gsfc.nasa.gov/data-access
class OpenURLWithEarthDataLogin(OpenURLWithFSSpec):
    def expand(self, *args, **kwargs):
        auth_kwargs = {}
        if 'EARTHDATA_LOGIN_TOKEN' in os.environ:
            auth_kwargs = {
                'headers': {'Authorization': f'Bearer {os.environ["EARTHDATA_LOGIN_TOKEN"]}'}
            }
        elif os.path.exists(os.environ.get('NETRC', os.path.expanduser('~/.netrc'))):
            # FIXME: Actually support the NETRC environment variable
            username, _, password = netrc.netrc().authenticators('urs.earthdata.nasa.gov')
            auth_kwargs = {'auth': aiohttp.BasicAuth(username, password)}
        if auth_kwargs:
            if self.open_kwargs is None:
                self.open_kwargs = auth_kwargs
            else:
                self.open_kwargs.update(auth_kwargs)
        return super().expand(*args, **kwargs)


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
        store_name=f'gpm-3imergdl',
        target_chunks={'time': 16},
        combine_dims=pattern.combine_dim_keys,
    )
)

