# DS2000-PCB rev A — mechanical reference

`DS2000-PCB-revA.step` is the populated rev A board, exported from
[DS2000-PCB](https://github.com/Mechanix97/DS2000-PCB) at commit `f9ae589` (DS2000-PCB#29, the
production review; re-export and update this line if the board changes before it is merged) with:

```sh
kicad-cli pcb export step --user-origin 100x94mm --subst-models -o DS2000-PCB-revA.step DS2000.kicad_pcb
```

It includes every part, the three Choc V1 switches with an MBK-style keycap on each, and the USB-C receptacle
underneath. Re-export it whenever the board's outline, holes or parts change, and note the PCB
commit here: the enclosure and the board share these numbers.

## Axes

Same as the STEP, so the file drops into Fusion 360 without moving it:

- **origin**: the board's centre, on its **bottom** face
- **X** to the right, seen from the user
- **Y** towards the **back** (the USB-C edge); the user sits at −Y
- **Z** up; the board's top face is at Z = 1.6

## Board

| | |
|---|---|
| Outline | 72 × 46 mm, X −36…+36, Y −23…+23, 3 mm corner radius |
| Thickness | 1.6 mm (4 layers) |
| Top face | black soldermask, the product's visible face: logos, key legends, the RP2350A on show |

## Mounting holes

Four M2, plated, tied to GND (the screws ground the tray's metal hardware if any).

| Hole | X | Y |
|---|---|---|
| H1 back left | −32 | +19 |
| H2 back right | +32 | +19 |
| H3 front left | −32 | −19 |
| H4 front right | +32 | −19 |

Drill 2.2 mm, copper ring 4.4 mm on both faces: keep screw heads and standoffs within 4.4 mm.

## Keys

| Key | Centre X | Centre Y |
|---|---|---|
| MUTE | −18 | −7.0 |
| DEAFEN | 0 | −7.0 |
| DISCONNECT | +18 | −7.0 |

- Kailh Choc V1 (low profile), soldered, no plate: the switch housing sits on the board's top face
  (13.8 mm lower housing, 15 mm flange 2.2 mm up, housing top at Z ≈ 6.6)
- keycap: MBK-style, 17.5 × 16.5 mm, 18 mm pitch, top at **Z ≈ 10.3** (1.6 board + ~8.7; real
  caps vary by a few tenths), 3 mm of travel
- the keys are fully exposed: nothing of the enclosure should rise above the board's top face
  within a keycap's footprint plus ~1 mm

## Underneath (what the tray has to clear)

| Item | Where | Below the board (Z) |
|---|---|---|
| USB-C receptacle | X −4.47…+4.47, Y +16.9…+24.2 (face 1.2 mm past the back edge) | 0 … **−3.35** |
| Choc switch pins and posts | under each key | 0 … −3.0 (centre hole Ø4.0, side posts Ø1.9) |
| MX switch pins (prototypes only) | two per key, at (+2.54, +5.08) and (−3.81, +2.54) from its centre | about 0 … −1.7 |
| Debug pads (SWD: TP1–TP3; BOOT: JP1; RST: JP2) | X +17.3…+24.5, Y +12.3…+17.8 | flat pads |
| Test pads TP4–TP6 (+5V, +3V3, +1V1) | X +4.9…+12.4, Y +5.3…+11.1 | flat pads |
| USB wire pads (J3), SMD | X −16.9…−7.7, Y +19.1…+22.1 | flat pads, plus the soldered cable |

- **Pocket depth**: at least **4 mm** under the whole board (USB-C plus margin), more if a weight or
  foam goes underneath
- **Back wall**: a cut-out for the USB-C plug's overmould, centred on X = 0, Z ≈ −1.7 (the
  receptacle's centre); overmoulds are commonly up to 12.5 × 6.5 mm, so leave at least 13 × 7 mm
- **Debug pads** are covered by the tray. Either the board comes off to reach them, or a small window
  goes under X +16…+25, Y +11…+19. TP4–TP6 are production test pads, outside that window
- If J3 is used (a soldered cable instead of the receptacle), its pads sit 1.2–10 mm left of the USB-C
  cut-out (X ±6.5): the cable turns inside the pocket and leaves through the same cut-out
- The key LEDs (SK6805-EC20) are on the **top** face, inside each switch's LED window (X −18 and 0,
  Y −11.7); nothing of them is underneath
