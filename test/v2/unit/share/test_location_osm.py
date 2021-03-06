"""Tests location data resource workers
"""

# standard imports
import logging

# third party imports
import pytest

# platform imports
import config
from server import db
from share.models.location import Location
from share.location import osm
from share.location.enum import LocationExternalSourceEnum

logg = logging.getLogger(__file__)


class LocationCacheControl:
    """callback function used in osm.resolve_name to check if record already exists in database

    Attributes
    ----------
    place_id : int
        the place_id of the encountered existing record
    location : Location
        the location object corresponding to the existing record
    """
    def __init__(self):
        self.osm_id = 0
        self.location = None


    def have_osm_data(self, osm_id):
        """Callback function used in osm.resolve_name to check if a record with osm place_id already exists.

        If a match is found, the osm_id and location is stored in the object.

        Parameters
        ----------
        place_id : int
            osm_id to check the database for

        Returns
        -------
        location : Location
            matched location object, None of no match
        """
        if self.location != None:
            raise RuntimeError('cached location already set')
        self.location = Location.get_by_custom(LocationExternalSourceEnum.OSM, 'osm_id', osm_id)
        if self.location != None:
            self.osm_id = osm_id
        return self.location



# TODO: improve by using object to hold cached location item which has have_osm_data as class method
def store_osm_data(location_data, cache):
    """Commits to database hierarchical data retrieved from the osm name resolve tool
       
    Parameters
    -----------
    location_data : dict
        location data as returned from osm.resolve_name
    cache : LocationCacheControl
        provides callback function used in osm.resolve_name to check if record already exists in database
         
    Returns
    -------
    locations : list
        list of location objects added to database
    """

    locations = []

    for i in range(len(location_data)):
        location = None
        if cache.location != None:
            if location_data[i]['ext_data']['osm_id'] == cache.osm_id:
                location = Location.get_by_custom(LocationExternalSourceEnum.OSM, 'osm_id', location_data[i]['ext_data']['osm_id'])
        if location == None:
            location = Location(
                location_data[i]['common_name'],
                location_data[i]['latitude'],
                location_data[i]['longitude'],
                    )
            location.add_external_data(LocationExternalSourceEnum.OSM, location_data[i]['ext_data'])
        locations.append(location)
    
    for i in range(len(locations)):
        location = locations[i]
        if location.location_external[0].external_reference['osm_id'] == cache.osm_id:
            break
        if i < len(locations)-1:
            locations[i].set_parent(locations[i+1])
        db.session.add(locations[i])
    db.session.commit()
    return locations



def test_get_osm_cascade(test_client, init_database):
    """
    GIVEN a search string
    WHEN hierarchical matches exist in osm for that string
    THEN check that location and relations are correctly returned
    """

    cache = LocationCacheControl()
    q = 'mnarani'
    q_countried = q + '  kenya'
    locations_data = osm.resolve_name(q_countried, storage_check_callback=cache.have_osm_data)
    location_data = locations_data[0]
    locations = store_osm_data(location_data, cache)
    
    leaf = locations[0]
    assert leaf != None
    assert leaf.common_name.lower() == q

    parent = leaf.parent
    assert parent.common_name.lower() == 'kilifi'

    parent = parent.parent
    assert 'kenya' in parent.common_name.lower() 



def test_get_osm_cascade_coordinates(test_client, init_database):
    """
    GIVEN coordinates
    WHEN hierarchical matches exist in osm for that coordinates
    THEN check that location and relations are correctly returned
    """

    cache = LocationCacheControl()
    r = 'mnarani'
    latitude = -3.6536
    longitude = 39.8512
    location_data = osm.resolve_coordinates(latitude, longitude, storage_check_callback=cache.have_osm_data)
    locations = store_osm_data(location_data, cache)

    leaf = locations[0]
    assert leaf != None
    assert leaf.common_name.lower() == r

    parent = leaf.parent
    assert parent.common_name.lower() == 'kilifi'

    parent = parent.parent
    assert 'kenya' in parent.common_name.lower() 


def test_get_osm_id(test_client, init_database):
    """
    GIVEN coordinates
    WHEN hierarchical matches exist in osm for that coordinates
    THEN check that location and relations are correctly returned
    """

    cache = LocationCacheControl()
    osm_id = 1396492751
    location_data = osm.resolve_id(osm_id, storage_check_callback=cache.have_osm_data)
    locations = store_osm_data(location_data, cache)

    leaf = locations[0]
    assert leaf != None
    assert leaf.common_name.lower() == "banjat e benjës"
