# SEO Images Generator

This script generates all required SEO and PWA images for the AAIP Data Tracker application.

## Generated Images

The script creates 5 images in `frontend/public/`:

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `og-image.png` | 1200x630 | Facebook/LinkedIn social sharing | ✅ |
| `twitter-card.png` | 1200x600 | Twitter social sharing | ✅ |
| `icon-192.png` | 192x192 | PWA icon (standard resolution) | ✅ |
| `icon-512.png` | 512x512 | PWA icon (high resolution) | ✅ |
| `logo.png` | 600x60 | Structured data logo | ✅ |

## Usage

```bash
# Generate all images
python3 scripts/generate_seo_images.py
```

## Requirements

- Python 3.x
- Pillow (PIL) library

Install Pillow if not available:
```bash
pip3 install Pillow
```

## Design Specifications

- **Primary Color**: #3b82f6 (Blue)
- **Secondary Color**: #1e40af (Darker Blue)
- **Text Color**: #ffffff (White)
- **Style**: Clean, professional, government application theme

## When to Regenerate

Regenerate images if:
- Brand colors change
- Logo/branding updates
- Text content needs modification
- Image quality needs improvement

## Integration

These images are automatically referenced in:
- `frontend/index.html` - Meta tags and Open Graph tags
- `frontend/public/manifest.json` - PWA configuration
- Sitemap and structured data

## SEO Impact

These images improve:
- Social media sharing appearance
- PWA installation experience
- Search engine understanding
- Mobile home screen icon quality
- Brand consistency across platforms

---

**Last Updated**: November 21, 2025
**Script Location**: `scripts/generate_seo_images.py`
