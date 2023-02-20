from prodigy.components.db import connect

db = connect()

examples = db.get_dataset("single-gold-all")
accept = [e for e in examples if e["answer"] == "accept"]
reject = [e for e in examples if e["answer"] == "reject"]
ignore = [e for e in examples if e["answer"] == "ignore"]

db.add_dataset("single-gold-accept")
db.add_dataset("single-gold-reject")
db.add_dataset("single-gold-ignore")

db.add_examples(accept, ["single-gold-accept"])
db.add_examples(reject, ["single-gold-reject"])
db.add_examples(ignore, ["single-gold-ignore"])
