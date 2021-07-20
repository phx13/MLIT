from flask import Blueprint, render_template, jsonify
from geopy.geocoders import Nominatim

from MLIT.models.gaz_name_model import GazNameModel
from MLIT.models.locality_model import LocalityModel
from MLIT.utils.geocoder_helper import GeocoderHelper
from MLIT.utils.io_helper import IOHelper
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
    model_path = 'MLIT/resources/models/machine_learning_model'
    nlp = NLPHelper.load_model(model_path)
    geolocator = Nominatim(user_agent='guoc9@cardiff.ac.uk', timeout=100)
    locations = []
    etl_locations = []
    for locality in localities:
        if locality[0]:
            doc = nlp(locality[0])
            for ent in doc.ents:
                if ent.label_ == 'GPE' and str(ent) not in locations:
                    locations.append(str(ent))
                    print(str(ent) + ' : ' + locality[0])
                    location = geolocator.geocode(ent)
                    etl_location = {GeocoderHelper.get_place_id(location): [str(GeocoderHelper.get_longitude(location)), str(GeocoderHelper.get_latitude(location)),
                                                                            GeocoderHelper.get_address(location)]}
                    etl_locations.append(etl_location)
    print(len(etl_locations))
    return jsonify(etl_locations)


@index_bp.route('/train/model/ruler/')
def training_model_ruler():
    try:
        original_data = GazNameModel.search_all_gaz_name()
        model_path = 'MLIT/resources/models/gaz_name_model'
        NLPHelper().train_model_ruler(original_data, model_path)
        return 'Train ruler model successful'
    except:
        return 'Train ruler model error'


@index_bp.route('/train/data/')
def training_data():
    try:
        model_path = 'MLIT/resources/models/gaz_name_model'
        data_path = 'MLIT/resources/data/TRAIN_DATA.json'
        original_data = [gaz_name['info_description'] for gaz_name in SerializationHelper.model_to_list(GazNameModel.search_all_gaz_name())]
        nlp = NLPHelper.load_model(model_path)
        NLPHelper.train_data(nlp, original_data, data_path)
        return 'Train data successful'
    except:
        return 'Train data error'


@index_bp.route('/train/model/machine_learning/')
def training_model_machine_learning():
    try:
        model_path = 'MLIT/resources/models/machine_learning_model'
        data_path = 'MLIT/resources/data/TRAIN_DATA.json'
        train_data = IOHelper.load_data(data_path)
        NLPHelper.train_model_machine_learning(train_data, 10, model_path)
        return 'Train machine learning model successful'
    except:
        return 'Train machine learning model error'
