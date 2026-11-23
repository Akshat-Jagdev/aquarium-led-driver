# India Suppliers — Aquarium V0 Project

> **Strategy**: Use LCSC for ICs and passives (cheapest, ships from China, 7-15 day delivery to India).
> Use Indian suppliers for mechanical parts, MCPCB, PSU, and large components.

---

## 1. Electronics (ICs, Passives, Connectors)

### LCSC (primary — cheapest, global)
- **Website**: https://www.lcsc.com
- **Shipping to India**: 7-15 days, free over $50 (₹4,000+)
- **Payment**: INR via Visa/Mastercard, or Wise, or PayPal
- **Search tip**: Use the part number directly in the search box
- **Bulk pricing**: 100+ pieces drops 30-50% on most parts
- **Quality**: Direct from manufacturer, genuine parts

**All LCSC parts and direct links are in `bom/lcsc_links.md`**

### Robu.in (Indian — fast delivery)
- **Website**: https://www.robu.in
- **Shipping**: 3-7 days within India
- **Payment**: INR, UPI, COD available
- **Stock**: ESP32 modules, dev boards, basic components
- **Best for**: ESP32-C3, breakout boards, switches, jacks

### QuartzComponents.com (Indian — broad)
- **Website**: https://quartzcomponents.com
- **Shipping**: 3-7 days
- **Best for**: Connectors, switches, basic passives
- **Payment**: INR, prepaid only

### Sunrom.com (Indian — industrial)
- **Website**: https://www.sunrom.com
- **Best for**: Power supplies, Mean Well products, industrial connectors
- **Payment**: INR, prepaid

### Evelta.in (Indian — Mean Well distributor)
- **Website**: https://evelta.in
- **Best for**: Mean Well PSUs, branded components
- **Payment**: INR, prepaid

### ConvertersIndia.com (Indian — Mean Well)
- **Website**: https://www.convertersindia.com
- **Best for**: Mean Well LRS series
- **Payment**: INR, prepaid

---

## 2. Power Supplies

### Mean Well LRS-35-24 (24V 1.5A 36W)
**Status**: Already ordered

**Indian distributors:**
- Sunrom: https://www.sunrom.com/p/mean-well-lrs-35-series
- Evelta: https://evelta.in/mean-well-lrs-35-24
- ConvertersIndia: https://www.convertersindia.com

**Bulk pricing (500 units):** ₹380-420 per unit
**Bulk pricing (1000 units):** ₹340-380 per unit
**Direct from Mean Well India:** Contact via https://www.meanwell.com

---

## 3. Aluminium MCPCB (LED Mounting)

### JLCPCB (China — fast, cheap, small batches)
- **Website**: https://jlcpcb.com
- **Capability**: Aluminium MCPCB, 1-4 layer, white soldermask
- **Lead time**: 3-5 days fabrication + 7-10 days shipping to India
- **Cost**: ₹70-100 per board for a 5-LED array (~140 × 20 mm, 1.6 mm thick)
- **Tool**: Use EDA tool (EasyEDA) or upload Gerber
- **MOQ**: 5 pieces (5 boards = ₹350-500)

### PCBWay (China — premium quality)
- **Website**: https://www.pcbway.com
- **Capability**: Aluminium MCPCB, ENIG finish, white soldermask
- **Lead time**: 5-7 days
- **Cost**: ₹90-150 per board

### Indian MCPCB manufacturers (better for 100+ units)
- **PCBPower** (Bangalore): https://www.pcbpower.com
- **LionCircuits** (Bangalore): https://www.lioncircuits.com
- **Cirexx** (India presence): https://www.cirexx.com
- **Epitome Components** (Pune): https://www.epitomeindia.com
- **Aaradhya Electronics** (Mumbai)

**Bulk pricing (500 units, 5-LED array):** ₹55-75 per board
**Bulk pricing (1000 units, 5-LED array):** ₹45-65 per board

### Driver PCB (FR4, 2-layer)
Same vendors as above. JLCPCB ₹150 for 5 PCBs (₹30 per board). Indian fab: ₹40-60 per board at 500 units.

---

## 4. Aluminium Extrusion (Heatsink/Housing)

### Local hardware stores (BEST for V0)
- Any major city has aluminium extrusion suppliers
- Search: "6063 aluminium extrusion 80x20mm" or similar
- Cost: ₹400-600 for 600mm length (1 unit)
- Bulk (500 units): ₹250-350 per 600mm piece

### Online India
- **IndiaMART**: https://www.indiamart.com (search "aluminium extrusion 6063")
- **TradeIndia**: https://www.tradeindia.com
- **Alibaba India**: https://www.alibaba.com (search suppliers with India warehouse)

### Specifications to ask for
- Alloy: **6063-T5** (good thermal conductivity, easy to machine)
- Cross-section: ~80mm × 20mm (wide and flat for good heat spread)
- Length: 600mm (V0) or 900mm (longer tanks)
- Surface: Mill finish or anodized black (anodized looks better, costs ₹50-100 more)
- Tolerance: ±0.2mm

---

## 5. Thermal Interface Material (TIM)

### Bergquist GP1500 (premium)
- Robu: https://www.robu.in (search "thermal pad")
- Mouser India: https://www.mouser.in
- Cost: ₹800-1200 per sheet (300×300mm, 0.5mm thick)
- Use 3-4 sheets for V0

### Generic 3W/mK silicone pad
- Robu, Amazon India, Flipkart
- Cost: ₹200-400 per sheet
- Adequate for V0

### Thermal paste (alternative to pad)
- Generic: ₹100-200 per syringe
- Arctic MX-4: ₹500-800
- Use thin layer between MCPCB and extrusion

---

## 6. Acrylic Diffuser

### Local plastic suppliers
- Search: "opal acrylic sheet 3mm" in your city
- Cost: ₹200-400 per 600×80mm sheet
- Bulk: ₹100-200 per sheet at 500 units

### Online India
- **IndiaMART**: https://www.indiamart.com
- **AcrylicSheetIndia**: https://www.acrylicsheets.in
- **SimplyAcrylic**: https://www.simplyacrylic.com

### Specifications
- Material: Cast acrylic (better optical quality than extruded)
- Colour: Opal/white (for V0; clear available for V1)
- Thickness: 3mm
- Light transmission: 60-70% (opal) or 92% (clear)

---

## 7. Mounting Brackets

### Adjustable aquarium light brackets
- **IndiaMART**: Search "aquarium light bracket adjustable"
- **Aquarium shops**: Most major cities have aquarium supply stores
- **Amazon India**: https://www.amazon.in (search "aquarium light bracket")
- Cost: ₹80-200 per pair (V0)
- Bulk: ₹50-100 per pair (500 units)

### DIY alternative (V0)
- Stainless steel L-brackets from hardware store
- Cost: ₹40-80 per pair
- Drill and bend to fit

---

## 8. End Caps (for extrusion)

### Option 1: 3D print (V0)
- Cost: ₹50-100 per pair (local 3D printing service)
- File source: Will provide STEP file when V0 is finalized
- Use PLA+ or PETG (NOT ABS for aquarium - off-gases)

### Option 2: Aluminium machined (production)
- Indian CNC shops: ₹80-150 per pair at 1 unit
- Bulk (500+): ₹30-60 per pair
- Anodize black to match extrusion

### 3D printing services in India
- **Imaginarium** (Mumbai, Bangalore): https://www.imaginarium.io
- **Objectify** (Delhi NCR): https://objectify.co.in
- **3Ding** (India-wide): https://www.3ding.in
- **Protomont** (Pune): https://www.protomont.com

---

## 9. Wiring and Connectors

### Silicone wire (22 AWG)
- Local electronic component shops
- Robu, Amazon India
- Cost: ₹100-200 per meter (multi-colour)

### JST-XH connectors (for LED-MCPCB connection)
- Robu, QuartzComponents
- 2.54mm pitch, 2-3 pin
- Cost: ₹5-10 per connector

### DC barrel jack (2.1mm)
- Robu, QuartzComponents
- Panel mount
- Cost: ₹30-50

### 24V→5V DC-DC module (IRM-02-5)
- Mouser India: https://www.mouser.in
- Element14 India: https://in.element14.com
- Digikey India: https://www.digikey.in
- Cost: ₹150-200 (1 unit)
- Bulk: ₹100-130 (500 units)

---

## 10. Testing Equipment (one-time purchase)

### Multimeter (essential)
- **Fluke 101** (₹2,500-3,500) or **Mastech MS8233E** (₹1,000-1,500)
- **Amazon India**: search "digital multimeter"
- Buy NOW if you don't have one

### Bench DC power supply (for prototype testing)
- **MCH-K305D** (₹3,500-5,000) — variable, current-limited
- **Amazon India**: search "bench DC power supply"
- Recommended for V0 development

### Clamp meter (for measuring PSU current)
- **Mastech MS2108** (₹1,500-2,500)
- **Amazon India**: search "AC DC clamp meter"

### K-type thermocouple + meter
- **Mastech MS6501** (₹2,000-3,000) or generic K-type + multimeter
- Required for thermal test (TP-04)

### Spectrometer (for V1)
- Defer purchase until V0 optical test is done
- **Recommended**: **UPRtek MK350N** (₹25,000-35,000) or **Asensetek Lighting Passport** (₹30,000-40,000)
- **Budget**: **HiPeak AS8030** (₹8,000-15,000) — adequate for V0

---

## 11. Order Strategy for V0

**Order these NOW (Phase B):**
1. **LCSC**: All ICs, passives, RSETs (parts 1-15 in BOM)
2. **Robu / Amazon IN**: ESP32 (already owned), barrel jack, rocker switch, fuse clips
3. **Sunrom / Evelta**: Mean Well LRS-35-24 (already owned)
4. **Local hardware store**: Aluminium extrusion, thermal pad
5. **Local plastic supplier**: Acrylic diffuser
6. **Aquarium shop or local hardware**: Mounting brackets

**Order these LATER (Phase C):**
1. **JLCPCB**: Driver PCB and MCPCBs (after KiCad design is done)

**Order these ONLY when ready:**
1. **Indian fab**: MCPCBs at 100+ unit volume
2. **Aluminium extrusion supplier**: Bulk order for 100+ units

---

## 12. Payment and Shipping Tips

- **UPI** is widely accepted in India and avoids credit card fees
- **COD** is available for Robu, Amazon IN
- **Bulk orders** (>₹25,000) usually get 5-15% extra discount — ask
- **GST invoice** needed for claiming ITC if you register a business
- **Shipping insurance** recommended for orders >₹10,000
