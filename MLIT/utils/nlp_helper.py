import random

import spacy
from spacy.lang.en import English
from spacy.training import Example

from MLIT.utils.io_helper import IOHelper
from MLIT.utils.serialization_helper import SerializationHelper


class NLPHelper:
    @staticmethod
    def load_model(model_path):
        return spacy.load(model_path)

    @staticmethod
    def train_model_ruler(original_data, model_path):
        gaz_names = []
        for data in SerializationHelper.model_to_list(original_data):
            gaz_names.append(data['name'])

        patterns = []
        for gaz_name in gaz_names:
            pattern = {'label': 'GPE', 'pattern': gaz_name}
            patterns.append(pattern)

        nlp = English()
        entity_ruler = nlp.add_pipe('entity_ruler')
        entity_ruler.add_patterns(patterns)
        nlp.to_disk(model_path)

    @staticmethod
    def train_data(nlp, original_data, data_path):
        train_data = []
        for data in original_data:
            if data:
                data = data.strip()
                doc = nlp(data)
                entities = []
                for ent in doc.ents:
                    entities.append((ent.start_char, ent.end_char, ent.label_))
                if len(entities) > 0:
                    results = [data, {'entities': entities}]
                    train_data.append(results)
        IOHelper.save_data(data_path, train_data)

    @staticmethod
    def train_model_machine_learning(train_data, iterations, model_path):
        nlp = spacy.blank("en")
        ner = nlp.create_pipe("ner")
        nlp.add_pipe('ner')
        ner.add_label("GPE")

        optimizer = nlp.initialize()
        for itn in range(iterations):
            print('time: ' + str(itn))
            random.shuffle(train_data)
            losses = {}
            for raw_text, entity_offsets in train_data:
                doc = nlp.make_doc(raw_text)
                example = Example.from_dict(doc, entity_offsets)
                nlp.update([example], drop=0.2, sgd=optimizer, losses=losses)
            print(losses)
        nlp.to_disk(model_path)
