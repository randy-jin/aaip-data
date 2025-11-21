#!/usr/bin/env python3
"""
Generate SEO-required images for AAIP Data Tracker
Creates 5 placeholder images with proper dimensions for social media and PWA
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand color
PRIMARY_COLOR = "#3b82f6"  # Blue
SECONDARY_COLOR = "#1e40af"  # Darker blue
TEXT_COLOR = "#ffffff"  # White

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_og_image(output_path):
    """Create Open Graph image (1200x630px) for Facebook/LinkedIn"""
    img = Image.new('RGB', (1200, 630), hex_to_rgb(PRIMARY_COLOR))
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw title
    title = "AAIP Data Tracker"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((600 - title_width//2, 200), title, fill=TEXT_COLOR, font=title_font)
    
    # Draw subtitle
    subtitle = "Real-time Alberta Immigration Program Analytics"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text((600 - subtitle_width//2, 320), subtitle, fill=TEXT_COLOR, font=subtitle_font)
    
    # Draw accent bar
    draw.rectangle([100, 450, 1100, 480], fill=hex_to_rgb(SECONDARY_COLOR))
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path}")

def create_twitter_card(output_path):
    """Create Twitter card image (1200x600px)"""
    img = Image.new('RGB', (1200, 600), hex_to_rgb(PRIMARY_COLOR))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 75)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    title = "AAIP Data Tracker"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((600 - title_width//2, 180), title, fill=TEXT_COLOR, font=title_font)
    
    subtitle = "Track Draws | Predict Scores | Stay Updated"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text((600 - subtitle_width//2, 290), subtitle, fill=TEXT_COLOR, font=subtitle_font)
    
    # Draw accent bar
    draw.rectangle([100, 420, 1100, 445], fill=hex_to_rgb(SECONDARY_COLOR))
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path}")

def create_pwa_icon(output_path, size):
    """Create PWA icon with specified size"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background
    margin = size // 10
    draw.rounded_rectangle(
        [margin, margin, size-margin, size-margin],
        radius=size//8,
        fill=hex_to_rgb(PRIMARY_COLOR)
    )
    
    # Draw "AAIP" text
    try:
        font_size = size // 3
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "AAIP"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text((size//2 - text_width//2, size//2 - text_height//2), text, fill=TEXT_COLOR, font=font)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path} ({size}x{size})")

def create_logo(output_path):
    """Create logo (600x60px) for structured data"""
    img = Image.new('RGB', (600, 60), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()
    
    text = "AAIP Data Tracker"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text((300 - text_width//2, 30 - text_height//2), text, fill=hex_to_rgb(PRIMARY_COLOR), font=font)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path}")

def main():
    # Get the frontend public directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    public_dir = os.path.join(project_root, 'frontend', 'public')
    
    # Ensure public directory exists
    os.makedirs(public_dir, exist_ok=True)
    
    print("🎨 Generating SEO images for AAIP Data Tracker...\n")
    
    # Create all required images
    create_og_image(os.path.join(public_dir, 'og-image.png'))
    create_twitter_card(os.path.join(public_dir, 'twitter-card.png'))
    create_pwa_icon(os.path.join(public_dir, 'icon-192.png'), 192)
    create_pwa_icon(os.path.join(public_dir, 'icon-512.png'), 512)
    create_logo(os.path.join(public_dir, 'logo.png'))
    
    print("\n✨ All SEO images generated successfully!")
    print(f"📁 Location: {public_dir}")
    print("\n📋 Generated files:")
    print("   1. og-image.png (1200x630) - Facebook/LinkedIn sharing")
    print("   2. twitter-card.png (1200x600) - Twitter sharing")
    print("   3. icon-192.png (192x192) - PWA icon")
    print("   4. icon-512.png (512x512) - PWA icon (high-res)")
    print("   5. logo.png (600x60) - Structured data logo")

if __name__ == "__main__":
    main()
