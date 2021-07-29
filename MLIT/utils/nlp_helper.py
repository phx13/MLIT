import random

import spacy
from spacy import Language
from spacy.lang.en import English
from spacy.training import Example

from MLIT.utils.io_helper import IOHelper


class NLPHelper:
    @staticmethod
    def load_model(model_path):
        return spacy.load(model_path)

    @staticmethod
    def add_pipeline(model, pipe):
        model.add_pipe(pipe, last=True)
        return model

    @staticmethod
    def train_model_ruler(locs, gpes, model_type, model_path):
        patterns = []
        for loc in locs:
            pattern = {'label': 'LOC', 'pattern': loc[0]}
            patterns.append(pattern)

        for gpe in gpes:
            pattern = {'label': 'GPE', 'pattern': gpe[0]}
            patterns.append(pattern)

        for direction in ['east', 'west', 'north', 'south', 'north-east', 'north-west', 'south-east', 'south-west']:
            pattern = {'label': 'DIR', 'pattern': direction}
            patterns.append(pattern)

        if model_type == 'Rule-based':
            nlp = English()
            entity_ruler = nlp.add_pipe('entity_ruler')
        else:
            nlp = spacy.load('en_core_web_sm')
            entity_ruler = nlp.add_pipe('entity_ruler', before='ner')
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
        nlp = English()
        ner = nlp.create_pipe('ner')
        nlp.add_pipe('ner', last=True)

        print(nlp.pipe_names)

        for _, annotations in train_data:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        print(other_pipes)
        with nlp.disable_pipes(*other_pipes):
            losses = []
            optimizer = nlp.initialize()
            for itn in range(iterations):
                print('time: ' + str(itn))
                random.shuffle(train_data)
                loss = {}
                examples = []
                for raw_text, entity_offsets in train_data:
                    doc = nlp.make_doc(raw_text)
                    example = Example.from_dict(doc, entity_offsets)
                    examples.append(example)

                    nlp.update([example], drop=0.2, sgd=optimizer, losses=loss)

                print(loss)
                scores = nlp.evaluate(examples)
                print(scores)

            print(losses)
            nlp.to_disk(model_path)

    @staticmethod
    @Language.component('advance_location')
    def advance_location(doc):
        new_ents = []
        for i in range(len(doc.ents)):
            if len(new_ents) > 0:
                break

            if doc.ents[i].label_ == 'LOC' and i == 0:
                print('find loc: ' + doc.ents[i].text)
                new_ents.append(doc.ents[i])
            elif doc.ents[i].label_ == 'LOC' and i != 0:
                # prev_token = doc[doc.ents[i].start - 1]
                # prev_ent = doc.ents[i - 1]
                # print(prev_ent.text + ' ' + prev_token.text + ' ' + doc.ents[i].text)
                # print(prev_ent.label_ + ' ' + prev_token.tag_ + ' ' + doc.ents[i].label_)
                # if prev_token.tag_ == 'IN' and prev_ent.label_ == 'DIR':
                #     print('find loc with direction: ' + prev_ent.text + ' ' + prev_token.text + ' ' + doc.ents[i].text)
                #     new_ents.append(prev_ent)
                #     new_ents.append(doc.ents[i])
                prev_token = doc[doc.ents[i].start - 1]
                prev_ent = doc.ents[i - 1]
                print(prev_ent.text + ' ' + prev_token.text + ' ' + doc.ents[i].text)
                print(prev_ent.label_ + ' ' + prev_token.tag_ + ' ' + doc.ents[i].label_)
                print(str(prev_ent.end) + ' ' + prev_token.tag_ + ' ' + str(doc.ents[i].start))
                if prev_ent.end == (doc.ents[i].start - 1) and prev_ent.label_ == 'DIR':
                    print('find loc with direction: ' + prev_ent.text + ' ' + prev_token.text + ' ' + doc.ents[i].text)
                    new_ents.append(prev_ent)
                    new_ents.append(doc.ents[i])
        doc.ents = new_ents
        return doc

# train_data = IOHelper.load_data('MLIT/resources/data/train/Model-Ruler Train.json')
# NLPHelper.train_model_machine_learning(train_data, 10, 'Model-Ruler Machine-learning', 'MLIT/resources/models/Model-Ruler Machine-learning')
