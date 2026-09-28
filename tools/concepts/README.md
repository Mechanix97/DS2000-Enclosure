# Concept models and renders

Parametric sketches (build123d) of the enclosure concepts in #1, rendered with pyvista. They are for
choosing a direction and fitting the board, not the final design, which is modelled in Fusion 360.

| Script | What |
|---|---|
| `concepts.py` | The three first concepts: A monolith, B frame, C floating |
| `concept_b_versions.py` | Concept B (chosen) flat and on a separate 7° wedge; exports `B_tray.step` and `B_wedge.step` |

The renders need a board STEP with the copper, mask and silkscreen:

```sh
kicad-cli pcb export step --user-origin 100x94mm --subst-models --include-tracks --include-pads \
  --include-zones --include-silkscreen --include-soldermask -o tools/concepts/pcb_render.step DS2000.kicad_pcb
pip install build123d pyvista
python tools/concepts/concept_b_versions.py pcb_render.step     # writes tools/concepts/out/
```
