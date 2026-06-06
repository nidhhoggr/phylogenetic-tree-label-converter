#!/usr/bin/env python3
"""
Generic phylogenetic tree SVG label converter with smart legend handling.
Version 2: Separates tree labels from legend labels.

Supports:
- Tree labels with IDs
- Legend showing clean organism names only
- Color-coded labels and legend
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional


class TreeLabelConverter:
    """Convert sequence identifiers in phylogenetic tree SVG files."""
    
    def __init__(self, mapping_config: Dict, verbose: bool = False):
        self.mapping_config = mapping_config
        self.verbose = verbose
        
        self.id_map = (
            mapping_config.get('id_mapping') or
            mapping_config.get('uniprot_to_subtype') or
            mapping_config.get('sequence_mapping') or
            mapping_config
        )
        self.replacements_made = {}
    
    def convert_svg_labels(self, svg_content: str, apply_colors: bool = True) -> str:
        """Replace identifiers in SVG text elements with mapped labels."""
        label_colors = (
            self.mapping_config.get('label_colors') or
            self.mapping_config.get('subtype_colors') or
            {}
        )
        
        text_element_pattern = r'(<text[^>]*>)([^<]+)(</text>)'
        
        def replace_text_element(match):
            opening_tag = match.group(1)
            original_text = match.group(2).strip()
            closing_tag = match.group(3)
            
            replacement_label = None
            replacement_color = None
            
            for test_id, mapped_label in self.id_map.items():
                if test_id.upper() in original_text.upper():
                    if self.verbose:
                        print(f"  ✓ {original_text} → {mapped_label}")
                    self.replacements_made[original_text] = mapped_label
                    replacement_label = mapped_label
                    
                    if apply_colors and mapped_label in label_colors:
                        replacement_color = label_colors[mapped_label]
                    break
            
            if replacement_label is None:
                return match.group(0)
            
            if replacement_color:
                if 'fill=' in opening_tag:
                    opening_tag = re.sub(r'fill="[^"]*"', f'fill="{replacement_color}"', opening_tag)
                else:
                    opening_tag = opening_tag.rstrip('>') + f' fill="{replacement_color}">'
            
            return f"{opening_tag}{replacement_label}{closing_tag}"
        
        updated_svg = re.sub(text_element_pattern, replace_text_element, svg_content)
        return updated_svg
    
    def add_legend_to_svg(self, svg_content: str) -> str:
        """Add legend using organism_names if available, otherwise label_colors."""
        # Try to use clean organism names for legend
        organism_names = self.mapping_config.get('organism_names', {})
        
        if organism_names:
            # Use clean organism names (no IDs) in legend
            legend_items = organism_names
            if self.verbose:
                print(f"  🎨 Using clean organism names for legend")
        else:
            # Fallback to label colors
            legend_items = (
                self.mapping_config.get('label_colors') or
                self.mapping_config.get('subtype_colors') or
                {}
            )
            if self.verbose:
                print(f"  🎨 Using label_colors for legend")
        
        if not legend_items:
            if self.verbose:
                print("  ℹ️  No legend data found, skipping legend")
            return svg_content
        
        # Extract viewBox dimensions
        viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
        if not viewbox_match:
            if self.verbose:
                print("  ⚠️  Could not find viewBox, skipping legend")
            return svg_content
        
        viewbox = viewbox_match.group(1)
        coords = list(map(float, viewbox.split(',')))
        width, height = coords[2], coords[3]
        
        # Create legend SVG group
        legend_y = height - 120
        legend_items_list = []
        
        for i, (label, color) in enumerate(legend_items.items()):
            y = legend_y + (i * 20)
            legend_items_list.append(
                f'<circle cx="20" cy="{y}" r="4" fill="{color}"/>\n'
                f'<text x="30" y="{y + 4}" font-family="Arial" font-size="11" '
                f'fill="#000000">{label}</text>'
            )
        
        legend = (
            f'<g id="legend">\n'
            f'<rect x="10" y="{legend_y - 10}" width="350" '
            f'height="{len(legend_items_list) * 20 + 10}" fill="#ffffff" '
            f'stroke="#cccccc" stroke-width="1" opacity="0.9"/>\n'
            f'{chr(10).join(legend_items_list)}\n'
            f'</g>'
        )
        
        svg_content = svg_content.replace('</svg>', f'\n{legend}\n</svg>')
        
        if self.verbose:
            print(f"  🎨 Added legend with {len(legend_items_list)} items")
        
        return svg_content


def load_mapping_config(config_file: str) -> Dict:
    """Load mapping configuration from JSON file."""
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert sequence IDs in phylogenetic tree SVG to meaningful names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python convert_tree_labels_v2.py tree.svg -c mapping.json
  
  # With legend and verbose
  python convert_tree_labels_v2.py tree.svg -c mapping.json -l -v
        '''
    )
    
    parser.add_argument('input_svg', help='Input phylogenetic tree SVG file')
    parser.add_argument('-o', '--output', help='Output SVG file', default=None)
    parser.add_argument('-c', '--config', help='Mapping configuration JSON file', default='config.json')
    parser.add_argument('-l', '--legend', action='store_true', help='Add color-coded legend')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed conversion information')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_svg)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input_svg}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_labeled{suffix}"
    
    try:
        if args.verbose:
            print(f"📖 Loading config: {args.config}")
        config = load_mapping_config(args.config)
        
        if args.verbose:
            print(f"📄 Loading SVG: {args.input_svg}")
        with open(input_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        if args.verbose:
            print(f"🔄 Converting labels...")
        converter = TreeLabelConverter(config, verbose=args.verbose)
        svg_content = converter.convert_svg_labels(svg_content, apply_colors=args.legend)
        
        if args.legend:
            if args.verbose:
                print(f"🎨 Adding legend...")
            svg_content = converter.add_legend_to_svg(svg_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"\n✅ Complete!")
        print(f"   Input:  {args.input_svg}")
        print(f"   Output: {output_path}")
        print(f"   Replaced: {len(converter.replacements_made)} labels")
        
        if args.verbose and converter.replacements_made:
            print(f"\n📋 Replacements made:")
            for original, replacement in sorted(converter.replacements_made.items()):
                print(f"   {original} → {replacement}")
    
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error in config: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
