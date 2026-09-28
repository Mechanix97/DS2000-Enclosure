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
- **Height**: keycap tops sit ~10.3 mm above the board's bottom face (Choc V1 + MBK); the tray adds to that

## Decided

- **Concept B, frame**: a bezel around the board with a lip 0.6 mm above its top face; the board sits
  recessed in it on four bosses (M2 into heat-set inserts). See [`concept-b-versions.png`](concept-b-versions.png)
- **Keys**: Kailh Choc V1 low profile with flat MBK-style caps, after the Chudx Nano 100 (DS2000-PCB#19)
- **Two versions of B, same tray**:
  - **flat**: the tray on rubber feet; the USB-C cable leaves straight back, level with the desk
  - **tilted**: the tray on a separate wedge, 7°, 3.0 mm at the front and 9.4 mm at the back, held by
    four 6 × 1.5 mm disc magnets under the corner bosses, with pockets matched in the wedge. The USB-C
    stays at the back and the cable leaves at 7°; a cable soldered to J3 is the alternative

## To decide

- [ ] Printer and process (FDM / resin), material (PLA, PETG, ASA…)
- [ ] Tray height under the board (6.5 mm in the concept: 4.5 mm pocket + 2 mm floor)
- [ ] Screws: M2 into heat-set inserts (as in the concept) or self-tapping into plastic
- [ ] Weight and grip: rubber feet, a steel or lead weight in the pocket (keys get pressed hard during
      calls)
- [ ] Access to the debug pads: take the board out, or a window in the floor
- [ ] Keycaps: MBK colour, and whether mute/deafen are translucent (their LEDs shine through the switch)
- [ ] Colour and finish of the tray, to go with the black-and-gold board

## Deliverables

- Fusion 360 archive in `cad/`, STEP of the enclosure and of the assembly in `step/`
- printable parts in `print/` with orientation and settings, and the hardware BOM (#6)
