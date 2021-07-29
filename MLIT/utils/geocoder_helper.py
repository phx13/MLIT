class GeocoderHelper:
    @staticmethod
    def get_osm_id(x):
        if hasattr(x, 'raw') and (x.raw is not None):
            return x.raw['osm_id']

    @staticmethod
    def get_address(x):
        if hasattr(x, 'address') and (x.address is not None):
            return x.address

    @staticmethod
    def get_latitude(x):
        if hasattr(x, 'latitude') and (x.latitude is not None):
            return x.latitude

    @staticmethod
    def get_longitude(x):
        if hasattr(x, 'longitude') and (x.longitude is not None):
            return x.longitude
