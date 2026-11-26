"""Reproduce the input read by either participant, even after later journal changes."""
import argparse
from itertools import islice
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import project_memory

PROJECT = '4i7-psus-2'
REVISION = 33
HEAD = '9156e1aec0dd09c4b6cbbb188e92d5cd2ecc1f6d793e410040fb41777ef77897'
SCOPE = 'experiment/001-entry'


def packet(variant):
    journal = ROOT / 'memory' / 'projects' / PROJECT / 'journal.jsonl'
    with tempfile.TemporaryDirectory() as temp, journal.open('rb') as stream:
        snapshot = Path(temp)
        (snapshot / 'journal.jsonl').write_bytes(b''.join(islice(stream, REVISION)))
        memory = project_memory.build_working_set(snapshot, PROJECT)
    if memory['revision'] != REVISION or memory['journal_head'] != HEAD:
        raise ValueError('Исходное состояние опыта отличается от сохранённой редакции')
    sources = {r['id']: r for r in memory['sources']}
    sections = []
    for source_id in ('S-BRIEF', 'S-REVISION', 'S-NOTE'):
        version = sources[source_id]['versions'][0]
        sections.append(f"{version['locator']} ({source_id}:v1)\n\n{version['content'].rstrip()}")
    if variant == 'B':
        sections.append('## Выдача памяти по карточке')
        for field, label in (('active_decisions','Действует'), ('historical_decisions','Заменено'), ('proposals','Предложено')):
            for r in memory[field]:
                if r['scope'] == SCOPE:
                    origins = ', '.join(f"{s['id']}:v{s['version']}" for s in r['source_refs'])
                    sections.append(f"{label} · {r['id']} · {origins}\n{r['text']}")
        card_ids = {r['id'] for r in memory['active_decisions'] if r['scope'] == SCOPE}
        for edge in memory['relations']:
            if card_ids.intersection([edge['from'], edge['to']]):
                sections.append(f"{edge['from']} {edge['kind']} {edge['to']}")
    return '\n\n'.join(sections)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=['A','B'])
    print(packet(parser.parse_args().variant))
