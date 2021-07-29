from flask import Blueprint, render_template, jsonify
from geopy.geocoders import Nominatim

from MLIT.models.gaz_name_model import GazNameModel
from MLIT.models.locality_model import LocalityModel
from MLIT.utils.common_helper import CommonHelper
from MLIT.utils.geocoder_helper import GeocoderHelper
from MLIT.utils.io_helper import IOHelper
from MLIT.utils.nlp_helper import NLPHelper
from MLIT.utils.serialization_helper import SerializationHelper

index_bp = Blueprint('index_bp', __name__)

models = {
    'Rule-based': 'MLIT/resources/models/Rule-based',
    'Model-Ruler': 'MLIT/resources/models/Model-Ruler',
    'Rule-based Machine-learning': 'MLIT/resources/models/Rule-based Machine-learning',
    'Model-Ruler Machine-learning': 'MLIT/resources/models/Model-Ruler Machine-learning',
}
datas = {
    'Rule-based': 'MLIT/resources/data/result/Rule-based.json',
    'Model-Ruler': 'MLIT/resources/data/result/Model-Ruler.json',
    'Rule-based Train': 'MLIT/resources/data/train/Rule-based Train.json',
    'Model-Ruler Train': 'MLIT/resources/data/train/Model-Ruler Train.json',
    'Rule-based Machine-learning': 'MLIT/resources/data/result/Rule-based Machine-learning.json',
    'Model-Ruler Machine-learning': 'MLIT/resources/data/result/Model-Ruler Machine-learning.json',
}


@index_bp.before_request
def before_request():
    pass


@index_bp.route('/')
def index_page():
    return render_template('index.html')


@index_bp.route('/test/')
def test_something():
    try:
        geolocator = Nominatim(user_agent='guoc9@cardiff.ac.uk', timeout=100)
        locations = geolocator.geocode('5km north of Walker County', exactly_one=False)
        etl_locations = []
        for location in locations:
            if 'New Zealand' in location.raw['display_name']:
                etl_locations.append(location.raw)
        print(etl_locations)
        return jsonify(etl_locations)

        # nlp = NLPHelper.load_model(models['ruler'])
        # doc = nlp('2.4 kilometers south-west Waitaki-Steward Road, 46 meters south of high terrace on east side of road.')
        # for ent in doc.ents:
        #     print(ent, ent.label_)
        # return 'Success'
    except:
        return 'Error'


@index_bp.route('/display/<data_type>/')
def display_location_data(data_type):
    try:
        etl_data = IOHelper.load_data(datas[data_type])
        return jsonify(etl_data)
    except:
        return 'Display data error'


@index_bp.route('/update/<model_type>/')
def update_location_data(model_type):
    localities = [(locality_data['Locality'], locality_data['East'], locality_data['North']) for locality_data in
                  SerializationHelper.model_to_list(LocalityModel.search_all_locality())]
    print(len(localities))

    geolocator = Nominatim(user_agent='guoc9@cardiff.ac.uk', timeout=100)

    model_path = models[model_type]
    nlp = NLPHelper.load_model(model_path)

    find_out_locations = []
    etl_locations = []

    # if not model_type.endswith('Machine-learning'):
    if 'advance_location' not in nlp.pipeline:
        nlp = NLPHelper.add_pipeline(nlp, 'advance_location')
    for locality in localities:
        if locality[0]:
            cleaned_text = locality[0].replace(',', ', ')
            cleaned_text = CommonHelper.replace_text([' N ', ' North '], ' north ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' S ', ' South '], ' south ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' E ', ' East '], ' east ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' W ', ' West '], ' west ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' NE ', ' N.E. '], ' north-east ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' NW ', ' N.W. '], ' north-west ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' SE ', ' S.E. '], ' south-east ', cleaned_text)
            cleaned_text = CommonHelper.replace_text([' SW ', ' S.W. '], ' south-west ', cleaned_text)
            doc = nlp(cleaned_text)
            if len(doc.ents) > 0:
                print(doc.ents)
                locations = []
                if len(doc.ents) == 1:
                    find_out_locations.append(doc.ents[0])
                    locations = geolocator.geocode(str(doc.ents[0]), exactly_one=False)
                    print(locations)
                elif len(doc.ents) == 2:
                    find_out_locations.append(doc.ents[1])
                    locations = geolocator.geocode(str(doc.ents[1]), exactly_one=False)
                    print(locations)

                if locations != None:
                    for location in locations:
                        if 'New Zealand' in location.raw['display_name']:
                            print(cleaned_text + ': ' + location.raw['display_name'] + '\n')
                            etl_location = {GeocoderHelper.get_osm_id(location): [str(GeocoderHelper.get_longitude(location)), str(GeocoderHelper.get_latitude(location)),
                                                                                  GeocoderHelper.get_address(location)]}
                            etl_locations.append(etl_location)
                            break
    # else:
    #     for locality in localities:
    #         if locality[0]:
    #             doc = nlp(locality[0])
    #             for ent in doc.ents:
    #                 if ent.label_ == 'LOC' and str(ent) not in find_out_locations:
    #                     print(str(ent))
    #                     find_out_locations.append(str(ent))
    #                     locations = geolocator.geocode(str(ent), exactly_one=False)
    #                     if locations != None:
    #                         for location in locations:
    #                             if 'New Zealand' in location.raw['display_name']:
    #                                 print(locality[0] + ': ' + location.raw['display_name'])
    #                                 etl_location = {GeocoderHelper.get_osm_id(location): [str(GeocoderHelper.get_longitude(location)), str(GeocoderHelper.get_latitude(location)),
    #                                                                                       GeocoderHelper.get_address(location)]}
    #                                 etl_locations.append(etl_location)
    #                                 break
    #                     break
    print(len(find_out_locations))
    print(len(etl_locations))

    final_statistic = {'total_count': len(localities), 'recognized_count': len(find_out_locations), 'geocoded_count': len(etl_locations), 'etl_locations': etl_locations}

    data_path = datas[model_type]
    IOHelper.save_data(data_path, final_statistic)
    return jsonify(final_statistic)


@index_bp.route('/train/model/<model_type>/')
def training_model(model_type):
    try:
        model_path = models[model_type]
        print(model_path)
        if model_type.endswith('Machine-learning'):
            data_path = datas[model_type.split()[0] + ' Train']
            train_data = IOHelper.load_data(data_path)
            NLPHelper.train_model_machine_learning(train_data, 10, model_path)
        else:
            locs = GazNameModel.search_all_locs()
            gpes = GazNameModel.search_all_gpes()
            NLPHelper.train_model_ruler(locs, gpes, model_type, model_path)
        return 'Train ' + model_type + ' model successful'
    except:
        return 'Train ' + model_type + ' model error'


@index_bp.route('/train/data/<data_type>/')
def training_data(data_type):
    try:
        model_path = models[data_type]
        data_path = datas[data_type + ' Train']
        original_data = [gaz_name['info_description'] for gaz_name in SerializationHelper.model_to_list(GazNameModel.search_all_gaz_name())]
        nlp = NLPHelper.load_model(model_path)
        NLPHelper.train_data(nlp, original_data, data_path)
        return 'Train ' + data_type + ' data successful'
    except:
        return 'Train ' + data_type + ' data error'
