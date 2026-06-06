# Phylogenetic Tree Label Converter

Generic tools for converting sequence identifiers in phylogenetic tree SVG visualizations to human-readable organism/species names with optional color-coding.

**Works with any organism** — just create a mapping configuration for your data.

## What's New (v4 Update)

✨ **NEW: Organism-level color grouping** — All variants of the same organism (e.g., all Zaire ebolavirus strains) now get the SAME color, regardless of strain information.

✨ **NEW: Fixed header parsing** — Correctly handles UniProt FASTA headers with `tr|` and `sp|` prefixes.

✨ **Color legends** — Automatically generates visual legends showing organism groups and their assigned colors.

## Files Included

### Scripts

- **`extract_organism_mapping.py`** - Generate mapping configuration from FASTA file
- **`convert_tree_labels.py`** - Apply mapping to phylogenetic tree SVG with optional colors

### Configuration Files

- **`config_template.json`** - Template for creating your own mapping config

## What It Does

The converter replaces cryptic sequence identifiers with meaningful organism/species names and optionally color-codes them by organism type.

### Before:

```
sp|Q66814|VGP_EBOSB
tr|A0A0N9QUW5|A0A0N9QUW5_9MONO
sp|O11457|VGP_EBOG4
tr|A0A3G2XDC4|A0A3G2XDC4_9MONO
```

### After (with colors):

```
Q66814 | Sudan ebolavirus (strain Boniface-76)          [Orange #E67E22]
A0A0N9QUW5 | Sudan ebolavirus                           [Orange #E67E22] ← SAME COLOR!
O11457 | Zaire ebolavirus (strain Gabon-94)            [Red #E74C3C]
A0A3G2XDC4 | Zaire ebolavirus                          [Red #E74C3C] ← SAME COLOR!
```

Notice: All Sudan variants share one color, all Zaire variants share another — even though they have different strains!

## Quick Start

### Step 1: Generate Mapping from FASTA

```bash
python3 extract_organism_mapping.py sequences_aligned.fasta -o mapping.json -v
```

This reads your FASTA file and creates a JSON mapping with:
- UniProt ID → Full organism name (including strain info)
- Colors grouped by base organism (strains ignored for color assignment)
- Organism legend

Output file `mapping.json` example:
```json
{
  "id_mapping": {
    "Q66814": "Q66814 | Sudan ebolavirus (strain Boniface-76)",
    "A0A0N9QUW5": "A0A0N9QUW5 | Sudan ebolavirus"
  },
  "label_colors": {
    "Q66814 | Sudan ebolavirus (strain Boniface-76)": "#E67E22",
    "A0A0N9QUW5 | Sudan ebolavirus": "#E67E22"
  },
  "organism_names": {
    "Sudan ebolavirus": "#E67E22"
  }
}
```

### Step 2: Convert Tree with Mapping

```bash
# Just labels, no colors
python3 convert_tree_labels.py tree.svg -c mapping.json

# With colors by organism group
python3 convert_tree_labels.py tree.svg -c mapping.json --color

# With colors AND legend
python3 convert_tree_labels.py tree.svg -c mapping.json --color -l

# Verbose output to see what's happening
python3 convert_tree_labels.py tree.svg -c mapping.json --color -l -v
```

This creates `tree_labeled.svg` with:
- Sequence IDs replaced with organism names
- Text labels colored by organism type
- Optional legend showing organism groups

## Usage Examples

### Generate mapping with verbose output

```bash
python3 extract_organism_mapping.py sequences.fasta -o config.json -v
```

Output shows:
```
📖 Reading FASTA file: sequences.fasta
✅ Success!
   Input:  sequences.fasta
   Output: config.json
   Sequences: 18
   Organism groups (ignoring strains): 6

📊 Summary:
   Total sequences: 18
   Organism groups: 6

   Bombali virus:
      - A0A4D5SG72 | Bombali virus
      ...

   Sudan ebolavirus:
      - Q66814 | Sudan ebolavirus (strain Boniface-76)
      - Q7T9D9 | Sudan ebolavirus (strain Human/Uganda/Gulu/2000)
      ...
```

### Apply to tree with all features

```bash
python3 convert_tree_labels.py tree.svg -c mapping.json --color -l -v
```

### Specify custom output filename

```bash
python3 convert_tree_labels.py tree.svg -c mapping.json -o my_custom_output.svg
```

## Configuration Format

### Minimal Config (manual)

```json
{
  "id_mapping": {
    "ID1": "Label 1",
    "ID2": "Label 2"
  }
}
```

### Full Config (with colors)

```json
{
  "description": "Ebolavirus mapping",
  "organism": "Ebolavirus",
  "id_mapping": {
    "Q66814": "Q66814 | Sudan ebolavirus (strain Boniface-76)",
    "O11457": "O11457 | Zaire ebolavirus (strain Gabon-94)"
  },
  "label_colors": {
    "Q66814 | Sudan ebolavirus (strain Boniface-76)": "#E67E22",
    "O11457 | Zaire ebolavirus (strain Gabon-94)": "#E74C3C"
  },
  "organism_names": {
    "Sudan ebolavirus": "#E67E22",
    "Zaire ebolavirus": "#E74C3C"
  }
}
```

### Key Features

- **Flexible key names**: The scripts support different naming conventions (`id_mapping`, `uniprot_to_subtype`, `sequence_mapping`, etc.)
- **Strain-aware grouping**: Automatically groups colors by base organism, stripping strain information from color assignment
- **Optional colors**: All color fields are optional; script works fine without them

## How It Works

### extract_organism_mapping.py

1. **Reads FASTA headers** in UniProt format:
   ```
   >sp|Q66814|VGP_EBOSB Envelope glycoprotein OS=Sudan ebolavirus (strain Boniface-76) OX=128948 ...
   ```

2. **Extracts**:
   - UniProt ID: `Q66814`
   - Full organism name: `Sudan ebolavirus (strain Boniface-76)`

3. **Groups by base organism**:
   - `Sudan ebolavirus (strain Boniface-76)` → Base: `Sudan ebolavirus`
   - `Sudan ebolavirus` → Base: `Sudan ebolavirus`
   - Both get **the same color**!

4. **Generates mapping JSON** with organism-grouped colors

### convert_tree_labels.py

1. **Reads SVG** and finds all text elements (labels)
2. **Extracts accession ID** from full UniProt labels
3. **Looks up** in mapping file
4. **Replaces** with human-readable name
5. **Applies color** to text (optional with `--color` flag)
6. **Adds legend** (optional with `-l` flag)

## Identifying Sequence IDs in Your Tree

### UniProt IDs (protein sequences)

Look for: `sp|Q66814|` or `tr|R4P4N7|`

- **sp**: SwissProt (curated, high-quality)
- **tr**: TrEMBL (translated, unreviewed)

### NCBI IDs (nucleotide or protein)

Look for: `NP_414542.1` or `NC_000001.1`

- **NP**: NCBI protein
- **NC**: NCBI nucleotide
- **NM**: NCBI mRNA

### Custom IDs

Any other identifier in your tree (local names, custom barcodes, etc.)

## Color Grouping by Organism

**Key Feature**: The tool intelligently groups colors by organism **type**, not by individual strains.

Example with Ebolavirus data:

| Organism | Variants | Count | Color |
|----------|----------|-------|-------|
| Zaire ebolavirus | (strain Gabon-94), plain | 4 | #E74C3C (red) |
| Sudan ebolavirus | (strain Boniface-76), (strain Human/Uganda/Gulu/2000), plain | 3 | #E67E22 (orange) |
| Reston ebolavirus | (strain Reston-89), plain | 3 | #F39C12 (gold) |
| Bombali virus | (3 variants) | 3 | #E74C3C (red) |
| Bundibugyo virus | (2 variants) | 2 | #3498DB (blue) |
| Tai Forest ebolavirus | (strain Cote d'Ivoire-94) | 1 | #34495E (dark gray) |

**All variants of Sudan ebolavirus** get the **same color**, regardless of which strain. This makes it easy to visually group related sequences on your tree!

## Creating Mappings for Different Organisms

### Automatic (recommended)

```bash
python3 extract_organism_mapping.py your_sequences.fasta -o your_mapping.json -v
```

### Manual (if needed)

1. Copy the template:
   ```bash
   cp config_template.json my_species_mapping.json
   ```

2. Edit with your IDs and species names

3. Use it:
   ```bash
   python3 convert_tree_labels.py tree.svg -c my_species_mapping.json --color -l
   ```

## Troubleshooting

### "No sequences found or could not parse headers"

**Cause**: Your FASTA headers don't match the expected UniProt format.

**Check**:
1. Do your headers start with `>sp|` or `>tr|`?
2. Do they have an `OS=` field?

**Example valid headers**:
```
>sp|Q66814|VGP_EBOSB Envelope glycoprotein OS=Sudan ebolavirus (strain Boniface-76) OX=128948
>tr|A0A0N9QUW5|A0A0N9QUW5_9MONO Envelope glycoprotein OS=Sudan ebolavirus OX=186540
```

### "0 labels replaced"

**Cause**: The UniProt IDs in your SVG don't match those in your mapping.

**Check**:
1. Run `extract_organism_mapping.py` on the SAME FASTA file used to generate the tree
2. Verify mapping.json has the right IDs
3. Run with `-v` flag to see what's being looked up

### Colors not appearing

**Check**:
1. Did you use the `--color` flag?
2. Is your mapping.json valid JSON?
3. Does it have a `label_colors` section?

## Python Requirements

- Python 3.6+
- **No external dependencies** — uses only standard library:
  - `json` — configuration parsing
  - `re` — pattern matching
  - `argparse` — CLI
  - `pathlib` — file handling

## Performance

- **Speed**: Instantly (milliseconds for typical trees)
- **SVG Size**: Unchanged
- **Memory**: Minimal (even 100MB SVGs load fine)

## License & Usage

Use freely for research and educational purposes. Attribution appreciated but not required.

## Examples in This Package

1. **Ebolavirus** (`config_template.json`)
   - 6 virus species with automatic color grouping
   - Ready to use

## Workflow Integration

### Typical bioinformatics pipeline

```bash
#!/bin/bash

# 1. Align sequences
mafft sequences.fasta > sequences_aligned.fasta

# 2. Build tree
fasttree -protein sequences_aligned.fasta > tree.newick

# 3. Visualize tree (generates tree.svg)
python3 your_tree_viz_tool.py tree.newick -o tree.svg

# 4. Generate mapping from same FASTA
python3 extract_organism_mapping.py sequences_aligned.fasta -o mapping.json

# 5. Convert tree labels and add colors
python3 convert_tree_labels.py tree.svg -c mapping.json --color -l

# 6. Output ready for publication!
echo "✅ Final tree: tree_labeled.svg"
```

## Questions?

1. Check help: `python3 convert_tree_labels.py --help`
2. Try examples first to understand format
3. Validate config JSON at [jsonlint.com](https://www.jsonlint.com)
4. Use `-v` (verbose) flag to debug

---

**For any organism. Any sequence identifier. Any phylogenetic tree. 🧬🌳**
