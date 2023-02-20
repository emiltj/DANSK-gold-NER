import spacy
from zshot import PipelineConfig, displacy
from zshot.linker import LinkerRegen
from zshot.mentions_extractor import MentionsExtractorSpacy
from zshot.utils.data_models import Entity

nlp = spacy.load("en_core_web_md")

# zero shot definition of entities
nlp_config = PipelineConfig(
    mentions_extractor=MentionsExtractorSpacy(),
    linker=LinkerRegen(),
    entities=[
        Entity(
            name="Paris",
            description="Paris is located in northern central France, in a north-bending arc of the river Seine",
        ),
        Entity(
            name="IBM",
            description="International Business Machines Corporation (IBM) is an American multinational technology corporation headquartered in Armonk, New York",
        ),
        Entity(name="New York", description="New York is a city in U.S. state"),
        Entity(name="Florida", description="southeasternmost U.S. state"),
        Entity(
            name="American",
            description="American, something of, from, or related to the United States of America, commonly known as the United States or America",
        ),
        Entity(
            name="Chemical formula",
            description="In chemistry, a chemical formula is a way of presenting information about the chemical proportions of atoms that constitute a particular chemical compound or molecul",
        ),
        Entity(
            name="Acetamide",
            description="Acetamide (systematic name: ethanamide) is an organic compound with the formula CH3CONH2. It is the simplest amide derived from acetic acid. It finds some use as a plasticizer and as an industrial solvent.",
        ),
        Entity(
            name="Armonk",
            description="Armonk is a hamlet and census-designated place (CDP) in the town of North Castle, located in Westchester County, New York, United States.",
        ),
        Entity(
            name="Acetic Acid",
            description="Acetic acid, systematically named ethanoic acid, is an acidic, colourless liquid and organic compound with the chemical formula CH3COOH",
        ),
        Entity(
            name="Industrial solvent",
            description="Acetamide (systematic name: ethanamide) is an organic compound with the formula CH3CONH2. It is the simplest amide derived from acetic acid. It finds some use as a plasticizer and as an industrial solvent.",
        ),
    ],
)
nlp.add_pipe("zshot", config=nlp_config, last=True)

text = (
    "International Business Machines Corporation (IBM) is an American multinational technology corporation"
    " headquartered in Armonk, New York, with operations in over 171 countries."
)

doc = nlp(text)
doc = nlp(
    "This is some other text that also contains information on hydrochloric acid (CH3COOH), which is sometimes used in medicine"
)
displacy.serve(doc, style="ent")

working = {
    "text": "Forhold til konventionen",
    "tokens": [
        {"text": "Forhold", "start": 0, "end": 7, "id": 0, "ws": true},
        {"text": "til", "start": 8, "end": 11, "id": 1, "ws": true},
        {"text": "konventionen", "start": 12, "end": 24, "id": 2, "ws": false},
    ],
    "_is_binary": false,
    "_view_id": "ner_manual",
    "answer": "accept",
    "_timestamp": 1635322276,
    "spans": [],
}

working = {
    "text": "Forhold til konventionen",
    "tokens": [
        {"text": "Forhold", "start": 0, "end": 7, "id": 0, "ws": true},
        {"text": "til", "start": 8, "end": 11, "id": 1, "ws": true},
        {"text": "konventionen", "start": 12, "end": 24, "id": 2, "ws": false},
    ],
    "_is_binary": false,
    "_view_id": "ner_manual",
    "answer": "accept",
    "_timestamp": 1635322276,
    "spans": [],
}


full = {
    "text": "Tredjegradsligninger",
    "tokens": [
        {"text": "Tredjegradsligninger", "start": 0, "end": 20, "id": 0, "ws": false}
    ],
    "_is_binary": false,
    "_view_id": "ner_manual",
    "answer": "accept",
    "_timestamp": 1635322276,
    "spans": [],
}


preds = {
    "text": "TEC 565",
    "tokens": [
        {"text": "TEC", "start": 0, "end": 3, "id": 0, "ws": true},
        {"text": "565", "start": 4, "end": 7, "id": 1, "ws": false},
    ],
    "_is_binary": false,
    "_view_id": "ner_manual",
    "answer": "accept",
    "_timestamp": 1635322276,
    "spans": [
        {"start": 4, "end": 7, "label": "PRODUCT", "token_start": 1, "token_end": 1}
    ],
}


l.keys()
l["versions"][0]
