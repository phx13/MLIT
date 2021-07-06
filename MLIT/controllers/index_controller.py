from flask import Blueprint, render_template, jsonify
from geopy.geocoders import Nominatim
from spacy.lang.en import English

from MLIT.models.location_model import LocationModel
from MLIT.utils.serialization_helper import SerializationHelper

geolocator = Nominatim(user_agent='guoc9@cardiff.ac.uk', timeout=100)

nlp = English()

index_bp = Blueprint('index_bp', __name__)


@index_bp.before_request
def before_request():
    pass


@index_bp.route('/')
def index_page():
    return render_template('index.html')


@index_bp.route('/data/')
def location_data():
    def get_place_id(x):
        if hasattr(x, 'place_id') and (x.place_id is not None):
            return x.place_id

    def get_address(x):
        if hasattr(x, 'address') and (x.address is not None):
            return x.address

    def get_latitude(x):
        if hasattr(x, 'latitude') and (x.latitude is not None):
            return x.latitude

    def get_longitude(x):
        if hasattr(x, 'longitude') and (x.longitude is not None):
            return x.longitude

    origin_locations = SerializationHelper.model_to_list([LocationModel.search_first_context()])
    etl_locations = []
    o_locations = nlp(origin_locations[0]['context'])
    for o_l in o_locations:
        location = geolocator.geocode(o_l.text.strip())
        etl_location = {get_place_id(location): [str(get_longitude(location)), str(get_latitude(location)), get_address(location)]}
        etl_locations.append(etl_location)
    return jsonify(etl_locations)
