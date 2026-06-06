#!/usr/bin/env python3
"""
Extract organism names from FASTA OS= field and create phylogenetic mapping config.
Version 3: IDs in tree labels, but legend shows clean virus names only.

Reads UniProt FASTA headers and extracts:
- UniProt ID (accession)
- Organism name from OS= field

Tree labels: "Q66814 | Sudan ebolavirus (strain Boniface-76)"
Legend shows: "Sudan ebolavirus (strain Boniface-76)" with color

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
    """
    id_match = re.search(r'\|([\w]+)\|', header)
    uniprot_id = id_match.group(1) if id_match else None
    
    os_match = re.search(r'OS=([^O]+?)(?:\s+OX=|$)', header)
    organism = os_match.group(1).strip() if os_match else "Unknown"
    
    return uniprot_id, organism


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
    Create phylogenetic mapping configuration.
    
    Tree labels include ID: "Q66814 | Sudan ebolavirus..."
    Legend colors map to clean organism names: "Sudan ebolavirus..."
    """
    # Create mapping with IDs for tree labels
    mapping_with_ids = {
        uniprot_id: f"{uniprot_id} | {organism}"
        for uniprot_id, organism in mapping.items()
    }
    
    # Get unique organisms for legend (without IDs)
    unique_organisms = sorted(set(mapping.values()))
    
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
    
    # Map clean organism names to colors
    organism_colors = {org: colors[i % len(colors)] 
                      for i, org in enumerate(unique_organisms)}
    
    # For the config, map tree labels to their organism colors
    label_colors = {}
    for uniprot_id, tree_label in mapping_with_ids.items():
        organism = mapping[uniprot_id]
        label_colors[tree_label] = organism_colors[organism]
    
    config = {
        "description": "Ebolavirus mapping extracted from sequence alignment",
        "source": "sequences_aligned.fasta",
        "organism": "Ebolavirus",
        "id_mapping": mapping_with_ids,
        "label_colors": label_colors if add_colors else {},
        "organism_names": organism_colors,  # Clean names for legend
    }
    
    return config


def print_summary(mapping: Dict[str, str]) -> None:
    """Print summary of extracted mappings."""
    unique_organisms = sorted(set(mapping.values()))
    
    print("\n" + "="*80)
    print("EXTRACTED VIRUS MAPPING (v3: IDs in tree, clean names in legend)")
    print("="*80)
    
    print(f"\nTotal sequences: {len(mapping)}")
    print(f"Unique organisms: {len(unique_organisms)}\n")
    
    org_counts = defaultdict(int)
    for org in mapping.values():
        org_counts[org] += 1
    
    print("Breakdown by organism:")
    for org in sorted(org_counts.keys()):
        print(f"  • {org}: {org_counts[org]} sequences")
    
    print("\nTree label format (ID | Organism):")
    for uniprot_id, organism in sorted(mapping.items()):
        print(f"  {uniprot_id} | {organism}")
    
    print("\nLegend will show clean organism names (no IDs)")
    print("\n" + "="*80 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Extract organism names from FASTA OS= field (v3: IDs in tree, clean legend)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Extract with IDs in tree, clean names in legend
  python extract_organism_mapping_v3.py sequences_aligned.fasta -o mapping.json
  
  # With verbose output
  python extract_organism_mapping_v3.py sequences_aligned.fasta -o mapping.json -v
        '''
    )
    
    parser.add_argument('fasta_file', help='Input FASTA file with UniProt headers')
    parser.add_argument('-o', '--output', help='Output JSON config file', default='organism_mapping.json')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed output')
    
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
        
        print(f"\n✅ Success!")
        print(f"   Input:  {args.fasta_file}")
        print(f"   Output: {output_path}")
        print(f"   Sequences: {len(mapping)}")
        print(f"   Unique organisms: {len(set(mapping.values()))}")
        
        if args.verbose:
            print_summary(mapping)
        
        print(f"\n💡 Use this config with tree converter:")
        print(f"   python convert_tree_labels_generic.py tree.svg -c {output_path} -l")
        print(f"\n📋 What you'll get:")
        print(f"   • Tree labels: ID | Virus Name (e.g., 'Q66814 | Sudan ebolavirus...')")
        print(f"   • Legend: Clean virus names only (no IDs)")
        print(f"   • Colors: Applied to both tree and legend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
