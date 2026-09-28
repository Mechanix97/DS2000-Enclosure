# DS2000-PCB rev A — mechanical reference

`DS2000-PCB-revA.step` is the populated rev A board, exported from
[DS2000-PCB](https://github.com/Mechanix97/DS2000-PCB) at commit `b65971f` (PR #18, rev A merged) with:

```sh
kicad-cli pcb export step --user-origin 100x94mm --subst-models -o DS2000-PCB-revA.step DS2000.kicad_pcb
```

It includes every part, the three MX switches with a 1u keycap on each, and the USB-C receptacle
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
| MUTE | −19.05 | −6.0 |
| DEAFEN | 0 | −6.0 |
| DISCONNECT | +19.05 | −6.0 |

- Cherry MX, PCB-mounted, no plate: the switch housing sits on the board's top face
- keycap: 18 × 18 mm at the base, top at **Z ≈ 21.3** (DSA/XDA-like profile in the model; real
  keycaps vary), 4 mm of travel
- the keys are fully exposed: nothing of the enclosure should rise above the board's top face
  within a keycap's footprint plus ~1 mm

## Underneath (what the tray has to clear)

| Item | Where | Below the board (Z) |
|---|---|---|
| USB-C receptacle | X −4.47…+4.47, Y +16.9…+24.2 (face 1.2 mm past the back edge) | 0 … **−3.35** |
| MX switch pins | under each key | 0 … −1.8 |
| SK6812MINI-E ×2 | under MUTE and DEAFEN (X −19.05 and 0, Y −11.1) | flush |
| Debug pads (SWD, BOOT, RST) | X +18…+23.1, Y +13…+17 | flat pads |
| USB wire holes (J3) | X −25.5…−17.9, Y +21 | through-holes |

- **Pocket depth**: at least **4 mm** under the whole board (USB-C plus margin), more if a weight or
  foam goes underneath
- **Back wall**: a cut-out for the USB-C plug's overmould, centred on X = 0, Z ≈ −1.7 (the
  receptacle's centre); overmoulds are commonly up to 12.5 × 6.5 mm, so leave at least 13 × 7 mm
- **Debug pads** are covered by the tray. Either the board comes off to reach them, or a small window
  goes under X +16…+25, Y +11…+19
- If J3 is used (soldered cable instead of the receptacle), the cable leaves from Y +21 near the back
  left and needs its own exit
