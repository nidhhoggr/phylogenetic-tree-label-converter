#!/usr/bin/env python3
"""
Extract organism names from FASTA OS= field and create phylogenetic mapping config.
Version 4: UPDATED - Colors grouped by organism subtype, NOT by strain

Reads UniProt FASTA headers and extracts:
- UniProt ID (accession)
- Organism name from OS= field

Tree labels: "Q66814 | Sudan ebolavirus (strain Boniface-76)"
Colors: All Sudan ebolavirus variants get SAME color (strains ignored)
Legend shows: Base organism names only (strain info stripped)

Outputs a JSON configuration file ready for tree label conversion.
"""

import re
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def extract_uniprot_header_info(header: str) -> Tuple[str, str]:
    """
    Extract UniProt ID and organism name from FASTA header.
    
    Format: tr|A0A4D5SG72|A0A4D5SG72_9MONO Envelope glycoprotein OS=Bombali virus OX=2010960
    """
    # Extract UniProt ID (tr|XXX| or sp|XXX|)
    id_match = re.search(r'\|([a-zA-Z0-9]+)\|', header)
    uniprot_id = id_match.group(1) if id_match else None
    
    # Extract organism name from OS= field
    os_match = re.search(r'OS=([^O]+?)(?:\s+OX=|$)', header)
    organism = os_match.group(1).strip() if os_match else "Unknown"
    
    return uniprot_id, organism


def extract_organism_group(organism: str) -> str:
    """
    Extract base organism name without strain information.
    
    Examples:
    - "Sudan ebolavirus (strain Boniface-76)" -> "Sudan ebolavirus"
    - "Zaire ebolavirus (strain Gabon-94)" -> "Zaire ebolavirus"
    - "Reston ebolavirus" -> "Reston ebolavirus"
    """
    # Remove strain information in parentheses
    base_organism = re.sub(r'\s*\(strain[^)]*\)', '', organism)
    return base_organism.strip()


def parse_fasta_headers(fasta_file: str) -> Dict[str, str]:
    """Parse FASTA file and extract UniProt ID -> Organism mapping."""
    mapping = {}
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                header = line[1:]
                uniprot_id, organism = extract_uniprot_header_info(header)
                
                if uniprot_id and organism:
                    mapping[uniprot_id] = organism
    
    return mapping


def create_config(mapping: Dict[str, str], add_colors: bool = True) -> Dict:
    """
    Create phylogenetic mapping configuration with strain-aware grouping.
    
    Tree labels include ID AND full organism name with strain:
        "Q66814 | Sudan ebolavirus (strain Boniface-76)"
    
    Colors grouped by BASE organism (ignoring strain):
        All Sudan variants -> same color
        All Zaire variants -> same color
    
    Legend shows BASE organism names only:
        "Sudan ebolavirus"
        "Zaire ebolavirus"
    """
    # Create mapping with IDs for tree labels (keep full organism name including strain)
    mapping_with_ids = {
        uniprot_id: f"{uniprot_id} | {organism}"
        for uniprot_id, organism in mapping.items()
    }
    
    # Get base organism names (without strain) for coloring
    base_organisms = {}
    for uniprot_id, organism in mapping.items():
        base = extract_organism_group(organism)
        base_organisms[uniprot_id] = base
    
    # Get unique base organisms for legend
    unique_base_organisms = sorted(set(base_organisms.values()))
    
    # Define color palette
    colors = [
        "#E74C3C",  # Red
        "#3498DB",  # Blue
        "#2ECC71",  # Green
        "#F39C12",  # Orange
        "#9B59B6",  # Purple
        "#1ABC9C",  # Teal
        "#E67E22",  # Dark Orange
        "#95A5A6",  # Gray
        "#34495E",  # Dark Gray
        "#F1C40F",  # Yellow
    ]
    
    # Map BASE organism names to colors
    organism_colors = {
        org: colors[i % len(colors)] 
        for i, org in enumerate(unique_base_organisms)
    }
    
    # For the config, map tree labels to their BASE organism colors
    label_colors = {}
    for uniprot_id, tree_label in mapping_with_ids.items():
        base_org = base_organisms[uniprot_id]
        label_colors[tree_label] = organism_colors[base_org]
    
    # Organism names for legend (base organisms only)
    organism_names = organism_colors
    
    config = {
        "description": "Phylogenetic mapping with organism grouping by subtype (strains grouped)",
        "source": "sequences_aligned.fasta",
        "organism": "Ebolavirus",
        "id_mapping": mapping_with_ids,
        "label_colors": label_colors if add_colors else {},
        "organism_names": organism_names if add_colors else {},
    }
    
    return config


def print_summary(mapping: Dict[str, str], show_grouping: bool = True):
    """Print summary of extracted organisms."""
    print(f"\n📊 Summary:")
    print(f"   Total sequences: {len(mapping)}")
    
    if show_grouping:
        # Group by base organism
        grouped = defaultdict(list)
        for uniprot_id, organism in mapping.items():
            base = extract_organism_group(organism)
            grouped[base].append((uniprot_id, organism))
        
        print(f"   Organism groups: {len(grouped)}")
        for base, variants in sorted(grouped.items()):
            print(f"\n   {base}:")
            for uniprot_id, full_org in sorted(variants):
                if full_org != base:
                    print(f"      - {uniprot_id} | {full_org}")
                else:
                    print(f"      - {uniprot_id} | {full_org}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract organism names from FASTA and create phylogenetic mapping config with organism grouping"
    )
    parser.add_argument(
        "fasta_file",
        help="Input FASTA file with UniProt headers"
    )
    parser.add_argument(
        "-o", "--output",
        default="organism_mapping.json",
        help="Output JSON config file (default: organism_mapping.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output showing organism grouping"
    )
    
    args = parser.parse_args()
    
    fasta_path = Path(args.fasta_file)
    if not fasta_path.exists():
        print(f"❌ Error: FASTA file not found: {args.fasta_file}")
        sys.exit(1)
    
    try:
        if args.verbose:
            print(f"📖 Reading FASTA file: {args.fasta_file}")
        
        mapping = parse_fasta_headers(str(fasta_path))
        
        if not mapping:
            print("❌ Error: No sequences found or could not parse headers")
            sys.exit(1)
        
        if args.verbose:
            print(f"🔧 Creating configuration...")
        
        config = create_config(mapping, add_colors=True)
        
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Count unique base organisms
        base_orgs = set()
        for organism in mapping.values():
            base_orgs.add(extract_organism_group(organism))
        
        print(f"\n✅ Success!")
        print(f"   Input:  {args.fasta_file}")
        print(f"   Output: {output_path}")
        print(f"   Sequences: {len(mapping)}")
        print(f"   Organism groups (ignoring strains): {len(base_orgs)}")
        
        if args.verbose:
            print_summary(mapping, show_grouping=True)
        
        print(f"\n💡 Use this config with tree converter:")
        print(f"   python convert_tree_labels.py tree.svg -c {output_path} --color -l")
        print(f"\n📋 What you'll get:")
        print(f"   • Tree labels: ID | Virus Name with strain (e.g., 'Q66814 | Sudan ebolavirus (strain Boniface-76)')")
        print(f"   • Colors: Grouped by organism subtype (strains with same base organism get same color)")
        print(f"   • Legend: Shows {len(base_orgs)} organism groups with colors")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
