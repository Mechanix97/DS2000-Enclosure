# Enclosure requirements

Draft for #2. The board side is fixed (see [`pcb/README.md`](../pcb/README.md)); the open items are
decisions for the enclosure itself.

## Fixed by the board

- **Concept**: the PCB is the visible top face; the enclosure is a tray underneath it. Nothing covers
  the face: the logos, key legends and the RP2350A are meant to be seen
- **Fixing**: four M2 screws through the board's corner holes (±32, ±19)
- **Footprint**: at least the board's 72 × 46 mm; the tray may extend past it (a lip or bezel) as
  long as it stays below the board's top face
- **Clearance underneath**: ≥ 4 mm pocket; USB-C cut-out in the back wall, ≥ 13 × 7 mm, centred on
  the receptacle
- **Height**: keycap tops sit ~21.3 mm above the board's bottom face; the tray adds to that

## To decide

- [ ] Printer and process (FDM / resin), material (PLA, PETG, ASA…)
- [ ] Tray height under the board, and whether the device sits flat or tilts towards the user
- [ ] Edge style: flush with the board, a visible lip/bezel around it, or a layered look
- [ ] Screws: M2 into heat-set inserts (recommended for repeat assembly) or self-tapping into plastic
- [ ] Weight and grip: rubber feet, a steel or lead weight in the pocket (keys get pressed hard during
      calls)
- [ ] Access to the debug pads: take the board out, or a window in the floor
- [ ] Keycaps: profile and whether mute/deafen are translucent (their LEDs shine through the switch)
- [ ] Colour and finish of the tray, to go with the black-and-gold board

## Deliverables

- Fusion 360 archive in `cad/`, STEP of the enclosure and of the assembly in `step/`
- printable parts in `print/` with orientation and settings, and the hardware BOM (#6)
