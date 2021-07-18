import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler

from MLIT.utils.serialization_helper import SerializationHelper


class NLPHelper:
    @staticmethod
    def load_gaz_names(db_data):
        gaz_names = []
        for data in SerializationHelper.model_to_list(db_data):
            gaz_names.append(data['name'])
        return gaz_names

    @staticmethod
    def create_training_data(gaz_names, label):
        patterns = []
        for gaz_name in gaz_names:
            pattern = {'label': label, 'pattern': gaz_name}
            patterns.append(pattern)
        return patterns

    @staticmethod
    def create_rule(patterns, path):
        nlp = English()
        entity_ruler = nlp.add_pipe('entity_ruler')
        entity_ruler.add_patterns(patterns)
        nlp.to_disk(path)

    def execute_training(self, db_data, path):
        gaz_names = self.load_gaz_names(db_data)
        patterns = self.create_training_data(gaz_names, 'GPE')
        self.create_rule(patterns, path)

    @staticmethod
    def load_model(path):
        return spacy.load(path)
