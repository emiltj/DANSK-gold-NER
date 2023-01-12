from typing import Iterator, Dict, Any
import spacy
from spacy.tokens import DocBin
from spacy.language import Language
from prodigy.components.preprocess import get_token, sync_spans_to_tokens
from pathlib import Path
import typer
import json


def main(
    # fmt: off
    path: Path = typer.Argument(..., help="Path to .spacy file"),
    spacy_model: str = typer.Argument(..., help="Name or path to spaCy pipeline or blank:en etc. for blank model, used to load DocBin"),
    include_ner: bool = typer.Option(False, "--ner", "-N", help="Include doc.ents as spans, if available"),
    include_textcat: bool = typer.Option(False, "--textcat", "-T", help="Include doc.cats as options, if available")
    # fmt: on
):
    """Load a binary .spacy file and output annotations in Prodigy's format."""
    nlp = spacy.load(spacy_model)
    doc_bin = DocBin().from_disk(path)
    examples = convert_examples(
        nlp, doc_bin, include_ner=include_ner, include_textcat=include_textcat
    )
    for eg in examples:
        print(eg)


def convert_examples(
    nlp: Language,
    doc_bin: DocBin,
    include_ner: bool = False,
    include_textcat: bool = False,
) -> Iterator[Dict[str, Any]]:
    docs = doc_bin.get_docs(nlp.vocab)
    for doc in docs:
        eg = {
            "text": doc.text,
            "tokens": [get_token(token, token.i) for token in doc],
            "_is_binary": False,
            "_view_id": "ner_manual",
            "answer": "accept",
            "_timestamp": 1635322276,
        }
        if include_ner:
            spans = [
                {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
                for ent in doc.ents
            ]
            eg["spans"] = sync_spans_to_tokens(spans, eg["tokens"])
        if include_textcat:
            eg["options"] = [{"id": cat, "text": cat} for cat in doc.cats]
            eg["accept"] = [cat for cat, score in doc.cats.items() if score == 1.0]
        yield json.dumps(eg)


if __name__ == "__main__":
    typer.run(main)
