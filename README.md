# Phylogenetic Tree Label Converter

Generic tools for converting sequence identifiers in phylogenetic tree SVG visualizations to human-readable organism/species names.

**Works with any organism** — just create a mapping configuration for your data.

## Files Included

### Scripts
- **`convert_tree_labels_generic.py`** - Generic Python script (organism-independent)
- **`convert_tree_labels.py`** - Original ebolavirus-specific script (deprecated, use generic version)

### Configuration Files
- **`config_template.json`** - Template for creating your own mapping config
- **`ebolavirus_mapping_updated.json`** - Example: Ebolavirus 6 species mapping
- **`example_mammals_mapping.json`** - Example: Mammalian species mapping
- **`example_bacteria_mapping.json`** - Example: Bacterial species mapping

## What It Does

The converter replaces cryptic sequence identifiers with meaningful organism/species names.

### Before:
```
sp|Q66814|VGP EBOSB
sp|P60173|VSGP EBOSM
NP_414542
tr|R4P4N7|R4P4N7 9MONO
```

### After:
```
Zaire ebolavirus (EBOV)
Sudan ebolavirus (SUDV)
Escherichia coli K-12 (E. coli)
Monogeneric Ebola-like virus
```

## Quick Start

### 1. Prepare Your Mapping

Create a JSON file with your sequence ID to name mappings:

```json
{
  "description": "Your organism",
  "id_mapping": {
    "SEQUENCE_ID_1": "Species Name (CODE)",
    "SEQUENCE_ID_2": "Another Species",
    "SEQUENCE_ID_3": "Third Species"
  },
  "label_colors": {
    "Species Name (CODE)": "#FF6B6B",
    "Another Species": "#4ECDC4",
    "Third Species": "#95E1D3"
  }
}
```

### 2. Run the Converter

```bash
python3 convert_tree_labels_generic.py your_tree.svg -c your_mapping.json
```

This creates: `your_tree_labeled.svg`

### 3. (Optional) Add a Legend

Include color-coded legend on the tree:

```bash
python3 convert_tree_labels_generic.py your_tree.svg -c your_mapping.json -l
```

## Usage Examples

### Basic Usage
```bash
python3 convert_tree_labels_generic.py tree.svg -c mapping.json
```

### Specify Output File
```bash
python3 convert_tree_labels_generic.py tree.svg -o output.svg -c mapping.json
```

### With Verbose Output
```bash
python3 convert_tree_labels_generic.py tree.svg -c mapping.json -v
```

### With Legend and Verbose
```bash
python3 convert_tree_labels_generic.py tree.svg -c mapping.json -l -v
```

### Get Help
```bash
python3 convert_tree_labels_generic.py --help
```

## Configuration Format

### Minimal Config
```json
{
  "id_mapping": {
    "ID1": "Label 1",
    "ID2": "Label 2"
  }
}
```

### Full Config (Recommended)
```json
{
  "description": "Descriptive title for your mapping",
  "organism": "Organism or group name",
  "id_mapping": {
    "UNIPROT_ID": "Full Species Name (ABBREVIATION)",
    "NCBI_ID": "Another Species",
    "CUSTOM_ID": "Local Sequence"
  },
  "label_colors": {
    "Full Species Name (ABBREVIATION)": "#HEX_COLOR",
    "Another Species": "#HEX_COLOR",
    "Local Sequence": "#HEX_COLOR"
  }
}
```

### Supported Key Names

The script is flexible and recognizes different configuration key names:

- **ID Mappings**: `id_mapping`, `uniprot_to_subtype`, `sequence_mapping`
- **Colors**: `label_colors`, `subtype_colors`

This allows existing configs to work without modification.

## Creating Mappings for Different Organisms

### For Ebolavirus (provided)
```bash
python3 convert_tree_labels_generic.py ebola_tree.svg -c ebolavirus_mapping_updated.json
```

### For Mammals (example)
```bash
# Edit example_mammals_mapping.json with your sequence IDs
python3 convert_tree_labels_generic.py primate_tree.svg -c example_mammals_mapping.json
```

### For Bacteria (example)
```bash
# Edit example_bacteria_mapping.json with your sequence IDs
python3 convert_tree_labels_generic.py pathogen_tree.svg -c example_bacteria_mapping.json
```

### For Your Own Organism
```bash
# 1. Copy the template
cp config_template.json my_species_mapping.json

# 2. Edit with your IDs and species names
# 3. Run converter
python3 convert_tree_labels_generic.py my_tree.svg -c my_species_mapping.json -v
```

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

## Finding Your Sequence IDs

### From UniProt
1. Go to [UniProt.org](https://www.uniprot.org/)
2. Search for your protein
3. Copy the accession number (first field)

### From NCBI
1. Go to [NCBI Protein](https://www.ncbi.nlm.nih.gov/protein/) or [NCBI Nucleotide](https://www.ncbi.nlm.nih.gov/nucleotide/)
2. Search for your sequence
3. Copy the accession number

### From Your Fasta File
```bash
# Extract just the IDs
grep "^>" sequences.fasta | cut -d' ' -f1 | sort -u

# This gives you all unique sequence headers to map
```

## Integration with Your Pipeline

### In Python
```python
from convert_tree_labels_generic import TreeLabelConverter, load_mapping_config

# Load config
config = load_mapping_config('mapping.json')

# Read tree SVG
with open('tree.svg') as f:
    svg_content = f.read()

# Convert labels
converter = TreeLabelConverter(config, verbose=True)
converted_svg = converter.convert_svg_labels(svg_content)

# Optionally add legend
converted_svg = converter.add_legend_to_svg(converted_svg)

# Save
with open('tree_labeled.svg', 'w') as f:
    f.write(converted_svg)
```

### In Shell Script
```bash
#!/bin/bash

# Typical bioinformatics pipeline
python scripts/pipeline.py -i sequences.fasta -o results

# Convert tree labels
python convert_tree_labels_generic.py \
  results/tree.svg \
  -o results/tree_for_publication.svg \
  -c config/organism_mapping.json \
  -l

echo "Tree ready for publication: results/tree_for_publication.svg"
```

## Color Scheme Tips

Use web-safe colors or hex codes. Here are some palettes:

### Pastel Palette
```
#FF6B6B #4ECDC4 #45B7D1 #FFA07A #95E1D3 #F38181 #AA96DA #FCBAD3
```

### Vibrant Palette
```
#FF0000 #00FF00 #0000FF #FFFF00 #FF00FF #00FFFF #FF8800 #8800FF
```

### Professional Palette
```
#264653 #2A9D8F #E9C46A #F4A261 #E76F51 #D5573B #845EC2 #B39DDB
```

## Adding to Your GitHub Repository

Recommended directory structure:

```
your-repo/
├── scripts/
│   ├── convert_tree_labels_generic.py
│   └── pipeline.py
├── config/
│   ├── config_template.json
│   ├── ebolavirus_mapping_updated.json
│   └── your_organism_mapping.json
└── README.md
```

Add to your workflow:
```bash
# Step in your pipeline documentation
5. Convert phylogenetic tree labels for publication:
   python scripts/convert_tree_labels_generic.py \
     results/tree.svg \
     -c config/organism_mapping.json -l
```

## Troubleshooting

### "No labels were replaced"
- Check that your SVG contains sequence IDs
- Verify IDs in mapping config match exactly (case-sensitive for most formats)
- Run with `-v` flag to see what the script is looking for

### "Config file not found"
- Check the path to your JSON file
- Use absolute paths: `/full/path/to/config.json`
- On Windows: use forward slashes or raw strings

### "Invalid JSON in config"
- Validate JSON at [jsonlint.com](https://www.jsonlint.com)
- Ensure all keys are quoted: `"id_mapping"` not `id_mapping`
- Trailing commas are not allowed in JSON

### Colors don't appear in legend
- Include `label_colors` in your config
- Use valid hex color codes: `#RRGGBB` format
- Run with `-l` flag to enable legend

### Tree looks wrong
- The converter only changes text labels, doesn't modify tree structure
- If branches/nodes are missing, the original SVG may be corrupted
- Check original SVG opens correctly before converting

## Python Requirements

- Python 3.6+
- **No external dependencies** — uses only standard library:
  - `json` — configuration parsing
  - `re` — pattern matching
  - `argparse` — CLI
  - `pathlib` — file handling

## Performance

- **Speed**: Instantly (milliseconds for typical trees)
- **SVG Size**: Unchanged (label length may vary slightly)
- **Memory**: Minimal (even 100MB SVGs load fine)

## License & Usage

Use freely for research and educational purposes. Attribution appreciated but not required.

## Examples in This Package

1. **Ebolavirus** (`ebolavirus_mapping_updated.json`)
   - 6 virus species with common names
   - Ready to use

2. **Mammals** (`example_mammals_mapping.json`)
   - Modify with your own NCBI IDs
   - Reference: NCBI Protein database

3. **Bacteria** (`example_bacteria_mapping.json`)
   - Modify with your own organism IDs
   - Reference: NCBI taxonomy

## Questions?

1. Check help: `python3 convert_tree_labels_generic.py --help`
2. Try example mappings first to understand format
3. Validate config JSON before running
4. Use `-v` (verbose) flag to debug

---

**For any organism. Any sequence identifier. Any phylogenetic tree. 🧬🌳**
