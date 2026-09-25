# The text pages at the front of the set: the CraftBot description below, then the run's brief.md,
# concept.md, design_notes.md and version_notes.md, flowed into four justified newsprint columns
# (tools/newsprint.py) at the largest type that fits two A2 pages, cut after the second. No title
# block. The agent team organigram (tools/organigram.py) and a QR code to the repository are on the
# first page. Called by fab_drawings.py.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'tools')))
from vector_pdf import THIN, HEAVY
from newsprint import Newsprint, parse, fit, FONT
from organigram import organigram
from title_blocks import qr
from qr_code import qr_matrix

RUN = os.path.normpath(os.path.join(HERE, '..', '..', 'GPT-6'))
DOCS = ['brief.md', 'concept.md', 'design_notes.md', 'version_notes.md']      # in order of priority
REPO = 'https://github.com/lukapiskorec/craftbot'
TITLE = 'CraftBot: Physical Prototyping Through Large Language Models'
DATELINE = ('CraftBot fabrication set', 'Experiment 16 - Expressive Structure, GPT-6 v02', 'September 2026')
MAX_PAGES = 2

CREDITS = '''
## Credits

The project author is Luka Piškorec, previously a lecturer at Aalto University and researcher at ETH Zürich, co-founder of TEN Studio (Zürich and Belgrade) and {protocell:labs} (Helsinki), practices that work at an intersection of architecture, design, digital art and research. CraftBot is part of the art-ai-fact initiative funded by Aalto University in 2025-2026.
'''

INTRO = '''
CraftBot is a harness for architect AI agents. It is agent-agnostic and can be used with any modern multi-modal LLM (Large Language Model). CraftBot reads a design brief, grounds itself in domain knowledge by ingesting documents, images and other references, and outputs Python code that defines a building procedurally. Instead of producing meshes or images, CraftBot writes scripts that construct architectural geometry in Blender. From there it can produce the industry's standard representations: floor plans, sections, elevations, BIM models, bills of quantities etc. It can run in a fully automated loop of code generation, execution, visual feedback and revision. The main research question is whether LLM agents can participate in architectural design when constrained to work through executable CAD code.

The project is documented through a GitHub repository holding code, iteration steps, references and outputs of the experiments done so far, enabling anyone to build on top of CraftBot. Construction manuals are included as extracted text summaries with links to the originals, which are left out for copyright reasons. Python and Blender were chosen for ease of access: both are open source, maintained, widely used, and free for commercial use.

Link to the repository: https://github.com/lukapiskorec/craftbot

You can view and manipulate the outputs of the previous CraftBot experiments using the online interface: https://lukapiskorec.github.io/craftbot

## Proof of concept: experiments

CraftBot was developed and tested through a series of fourteen experiments conducted between November 2025 and August 2026. Each experiment starts with a short design brief and reference files. The early experiments work from pictures alone: a carport with a king post truss, the same carport rebuilt with a gothic hammer beam truss, a small steel shelter, Jean Prouvé's demountable 6x6 house. The later ones add text sourced from reference manuals. Experiment 08 was given a 27-page special issue of The Architects' Journal from 1986 describing the Segal method of timber self-build, and produced a house in that method. Experiment 09 read a guide to cross-laminated timber and built a ten-storey block, while experiment 11 started from a Canadian manual on wood-frame house construction to produce a model of a hip roof.

After the input resources are read, the user-defined brief is interpreted and expanded into a building concept and subsequently modelled in Blender using Python code as procedural instructions. Then the agent uses the code to generate the 3D model of the building and takes screenshots of it using headless Blender: no Blender window is actually opened, the agent is able to run the whole rendering pipeline through a command line by itself. The screenshots are then evaluated by the agent and any deviations from the brief or mistakes in the model noted. The agent then goes back to refine the Python code, saving each version of the model as a design iteration until it converges with the brief.

In the first version of CraftBot (ChatGPT 5.1 as agent), this iterative improvement loop was manual and required human attention to execute. The new version with Fable as the agent is able to execute this loop in a fully autonomous manner. Although no human input is needed in principle, future experiments will test a more hybrid approach. Human input might help better guide the convergence of the model with the brief, especially in the later iterations of the design.

As of September 2026, the experiments are still ongoing and can be found on the project's GitHub page.

## Agent team

![organigram]

The most recent iteration of CraftBot (September 2026) implements a team of agents, each with its defined role, inputs, working procedures, and memory:

- **CraftBot**, orchestrator, writes down the brief as it understood it, decides what is in scope, compiles the design rationale document at the end and reports back to the user.
- **Designer** produces the spatial and construction concept and turns it into a numbered checklist of requirements, each one with its source and a way to test it.
- **Researcher** searches the manuals for what the concept needs, picks the chapters that apply, reads them and crops out the figures the Designer needs.
- **Builder** implements the concept as versioned Blender Python scripts, renders them and runs the automated checks for geometry overlap, floating elements etc.
- **Inspector** looks at the renders of the model, which it compares against the requirements and the reference materials, and reports what is missing, misplaced or unlike the reference.
- **Runner** works in the background, exporting each finished version to the web viewer and archiving the run.

The rule that holds the team together: every hand-off is a file on disk, never a chat message. Hand-off documents include the brief, concept, sources, requirements, design notes, version notes, inspection reports etc. Any agent can be terminated and restarted from those files, and the human reading afterwards gets the same record the agents worked from. To aid their work, agents use skills, documents that describe specially designed procedures to accomplish specific tasks, placed in the skills/ folder of the project repository. To ground their work in architectural domain knowledge, they consult expert manuals and guide documents, while reusable Python scripting tools are available in the tools/ folder. These materials and the resource structure form the backbone of the agent harness.

The pages that follow reproduce, unedited, the hand-off documents of this run: the brief as CraftBot understood it, the Designer's concept, the design notes and the Builder's version notes.
'''


def masthead(sheet, number):
    """The head of page `number`: the full masthead with the repository QR code on the first page,
    a running head on the others. Returns the y where the columns start."""
    m, w = 12.0, sheet.w
    if number > 1:
        sheet.text(m, sheet.h-m-4, TITLE, 3.0, font=FONT, italic=True)
        sheet.text(w-m, sheet.h-m-4, f'{DATELINE[1]}  ·  page {number}', 3.0, 'end', font=FONT)
        sheet.line((m, sheet.h-m-6), (w-m, sheet.h-m-6), THIN)
        return sheet.h-m-10
    top = sheet.h-m
    side = 22.0
    qr(sheet, qr_matrix(REPO), w-m-side, top-side, side)
    sheet.text(w-m-side/2, top-side-3.2, 'source code', 2.2, 'middle', font=FONT, italic=True)
    sheet.line((m, top-2), (w-m-side-8, top-2), HEAVY)
    sheet.line((m, top-3.2), (w-m-side-8, top-3.2), THIN)
    sheet.text((w-side-8)/2, top-16, TITLE, 8.0, 'middle', font=FONT, weight=700)
    sheet.line((m, top-20.5), (w-m-side-8, top-20.5), THIN)
    sheet.text(m, top-24.5, DATELINE[0].upper(), 2.4, font=FONT, spacing=0.3)
    sheet.text((w-side-8)/2, top-24.5, DATELINE[1].upper(), 2.4, 'middle', font=FONT, spacing=0.3)
    sheet.text(w-m-side-8, top-24.5, DATELINE[2].upper(), 2.4, 'end', font=FONT, spacing=0.3)
    sheet.line((m, top-26.5), (w-m, top-26.5), HEAVY)
    return top-31


def blocks():
    """The intro, the four run documents and the credits as newsprint blocks."""
    out = parse(INTRO)
    for name in DOCS:
        with open(os.path.join(RUN, name), encoding='utf-8') as f:
            out += parse(f.read())
    return out+parse(CREDITS)


def front_pages(sheets):
    """Lay the text out and add the pages to the set, before the drawings; returns the pages."""
    press = Newsprint(masthead, {'organigram': ('The CraftBot agent team, September 2026: who spawns whom, and what each hands back.', organigram)})
    size, pages, fill, cut = fit(press, blocks(), MAX_PAGES)
    print(f'front pages: {len(pages)} at {size:.2f} mm type, last page {fill:.0%} full' + (', text cut' if cut else ''))
    for i, page in enumerate(pages, 1):
        sheets.page(f'Text page {i}', page)
    return pages


if __name__ == '__main__':
    from vector_pdf import print_pdf
    press = Newsprint(masthead, {'organigram': ('The CraftBot agent team.', organigram)})
    size, pages, fill, cut = fit(press, blocks(), MAX_PAGES)
    print(f'{len(pages)} pages at {size:.2f} mm, last page {fill:.0%} full, cut={cut}')
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'front.pdf')
    for i, page in enumerate(pages, 1):
        with open(out.replace('.pdf', f'_{i}.svg'), 'w', encoding='utf-8') as f:
            f.write(page.svg())
    print_pdf(out, pages)
