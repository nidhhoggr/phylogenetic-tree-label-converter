#!/usr/bin/env python3
"""Phylogenetic Tree Label Converter"""

import json
import re
import argparse
from pathlib import Path


def load_mapping_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def extract_accession_id(label):
    match = re.match(r'^(?:sp|tr)\|([^|]+)\|', label)
    return match.group(1) if match else label


def extract_organism_group(label):
    """Extract the base organism name without strain info.
    
    Examples:
    - "Q7T9D9 | Sudan ebolavirus (strain Human/Uganda/Gulu/2000)" -> "Sudan ebolavirus"
    - "A0A1P8YTA8 | Zaire ebolavirus" -> "Zaire ebolavirus"
    - "B8XCN0 | Bundibugyo virus" -> "Bundibugyo virus"
    """
    if '|' not in label:
        return label
    
    organism = label.split('|', 1)[1].strip()
    # Remove strain info in parentheses
    organism = re.sub(r'\s*\(strain[^)]*\)', '', organism)
    return organism.strip()


class TreeLabelConverter:
    
    def __init__(self, config, verbose=False, add_colors=False):
        self.verbose = verbose
        self.add_colors = add_colors
        
        self.id_mapping = config.get('id_mapping') or config.get('uniprot_to_subtype') or config.get('sequence_mapping') or {}
        self.label_colors = config.get('label_colors') or config.get('subtype_colors') or {}
        self.organism_names = config.get('organism_names') or {}
        
        # Build organism group -> color mapping
        self.organism_to_color = {}
        for label, color in self.label_colors.items():
            group = extract_organism_group(label)
            if group not in self.organism_to_color:
                self.organism_to_color[group] = color
        
        if self.verbose:
            print(f"Loaded {len(self.id_mapping)} ID mappings")
            print(f"Loaded {len(self.label_colors)} color definitions")
            print(f"Organism groups: {len(self.organism_to_color)}")
            for org, color in sorted(self.organism_to_color.items()):
                print(f"  {org:40s} -> {color}")
    
    def convert_svg_labels(self, svg_content):
        """Convert all matching labels in SVG content."""
        replacements = 0
        
        # Find all label content blocks - process in reverse order to maintain positions
        pattern = r'>([^<]+?)<'
        matches = list(re.finditer(pattern, svg_content, flags=re.DOTALL))
        
        modified_content = svg_content
        offset = 0  # Track position offset as we make changes
        
        for match in reversed(matches):
            full_label = match.group(1).strip()
            accession_id = extract_accession_id(full_label)
            
            if accession_id not in self.id_mapping:
                continue
            
            new_label = self.id_mapping[accession_id]
            replacements += 1
            
            if self.verbose:
                print(f"  {accession_id:20s} -> {new_label[:50]:50s}", end="")
            
            # Replace the content
            start, end = match.span()
            
            # Make the replacement
            old_text = f">{full_label}<"
            new_text = f">{new_label}<"
            modified_content = modified_content[:start] + new_text + modified_content[end:]
            
            # Now find and modify the style attribute for this text element
            if self.add_colors:
                group = extract_organism_group(new_label)
                if group in self.organism_to_color:
                    color = self.organism_to_color[group]
                    
                    # Look backwards from start position to find the matching <text tag and its style
                    search_start = max(0, start - 200)
                    search_region = modified_content[search_start:start]
                    
                    # Find the style="stroke:none;" in this region
                    style_match = re.search(r'style="stroke:none;"', search_region)
                    if style_match:
                        style_start = search_start + style_match.start()
                        style_end = style_start + len('style="stroke:none;"')
                        modified_content = (modified_content[:style_start] + 
                                          f'style="stroke:none;fill:{color};"' +
                                          modified_content[style_end:])
                        if self.verbose:
                            print(f" [{group:30s}] {color}")
                    else:
                        if self.verbose:
                            print()
                else:
                    if self.verbose:
                        print(f" [no color for {group}]")
            else:
                if self.verbose:
                    print()
        
        self.replacements = replacements
        return modified_content
    
    def add_legend_to_svg(self, svg_content):
        if not self.organism_to_color:
            return svg_content
        
        legend_svg = '\n<!-- Color Legend by Organism Group -->\n<g id="legend" transform="translate(20, 20)" style="font-size: 9px; font-family: sans-serif;">\n'
        
        y_offset = 0
        for org, color in sorted(self.organism_to_color.items()):
            legend_svg += f'  <rect x="0" y="{y_offset}" width="12" height="12" style="fill:{color};stroke:black;stroke-width:0.5"/>\n'
            legend_svg += f'  <text x="18" y="{y_offset + 10}" style="fill:black;">{org}</text>\n'
            y_offset += 15
        
        legend_svg += '</g>\n'
        # Insert before </svg> (the closing svg tag might be on its own line or with >\n)
        return re.sub(r'</svg[^>]*>', legend_svg + '</svg>', svg_content)


def main():
    parser = argparse.ArgumentParser(description="Convert sequence IDs in phylogenetic tree SVGs to organism names")
    parser.add_argument("svg_file", help="Input SVG file")
    parser.add_argument("-c", "--config", required=True, help="Mapping config JSON file")
    parser.add_argument("-o", "--output", help="Output SVG file")
    parser.add_argument("-l", "--legend", action="store_true", help="Add legend to output")
    parser.add_argument("--color", action="store_true", help="Color text labels by organism group (ignoring strains)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        config = load_mapping_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Config error: {e}")
        return 1
    
    try:
        with open(args.svg_file, 'r') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print(f"❌ SVG file not found: {args.svg_file}")
        return 1
    
    converter = TreeLabelConverter(config, verbose=args.verbose, add_colors=args.color)
    converted_svg = converter.convert_svg_labels(svg_content)
    
    if args.legend:
        converted_svg = converter.add_legend_to_svg(converted_svg)
    
    output_path = args.output or str(Path(args.svg_file).parent / f"{Path(args.svg_file).stem}_labeled.svg")
    
    with open(output_path, 'w') as f:
        f.write(converted_svg)
    
    print(f"✅ Complete!")
    print(f"   Input:  {args.svg_file}")
    print(f"   Output: {output_path}")
    print(f"   Replaced: {converter.replacements} labels")
    if args.color:
        print(f"   Colors: Applied by organism group (strains grouped together)")
    if args.legend:
        print(f"   Legend: Added")
    
    return 0


if __name__ == "__main__":
    exit(main())
