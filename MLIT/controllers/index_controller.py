from flask import Blueprint, render_template, jsonify
from geopy.geocoders import Nominatim

from MLIT.models.gaz_name_model import GazNameModel
from MLIT.models.locality_model import LocalityModel
from MLIT.utils.geocoder_helper import GeocoderHelper
from MLIT.utils.nlp_helper import NLPHelper
from MLIT.utils.serialization_helper import SerializationHelper

index_bp = Blueprint('index_bp', __name__)


@index_bp.before_request
def before_request():
    pass


@index_bp.route('/')
def index_page():
    return render_template('index.html')


@index_bp.route('/data/')
def location_data():
    localities = [(locality_data['Locality'], locality_data['East'], locality_data['North']) for locality_data in
                  SerializationHelper.model_to_list(LocalityModel.search_all_locality())]
    nlp = NLPHelper.load_model('MLIT/resources/models/gaz_name_model')
    geolocator = Nominatim(user_agent='guoc9@cardiff.ac.uk', timeout=100)
    etl_locations = []
    for locality in localities:
        if locality[0]:
            doc = nlp(locality[0])
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    print(str(ent) + ' : ' + locality[0])
                    location = geolocator.geocode(ent)
                    etl_location = {GeocoderHelper.get_place_id(location): [str(GeocoderHelper.get_longitude(location)), str(GeocoderHelper.get_latitude(location)),
                                                                            GeocoderHelper.get_address(location)]}
                    etl_locations.append(etl_location)
    print(etl_locations)
    return jsonify(etl_locations)


@index_bp.route('/train/')
def train_data():
    try:
        db_data = GazNameModel.search_all_gaz_name()
        path = 'MLIT/resources/models/gaz_name_model'
        NLPHelper().execute_training(db_data, path)
        return 'Train successful'
    except:
        return 'Train error'
