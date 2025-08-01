# PowerPoint Generator

A Python-based tool for creating PowerPoint presentations programmatically using the `python-pptx` library.

## Features

- 🎯 **Multiple Slide Types**: Title slides, bullet points, two-column layouts, text slides, section dividers, and image slides
- 📊 **JSON Configuration**: Define your presentation structure in a simple JSON format
- 🎨 **Professional Styling**: Clean, modern layouts with proper formatting
- 🔧 **Customizable**: Easy to modify and extend for specific needs
- 📱 **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start - Create a Sample Presentation

```bash
python ppt_generator.py --sample
```

This creates a `presentation.pptx` file with a sample presentation demonstrating all available features.

### Create Custom Presentations

#### Method 1: Use JSON Configuration

1. Create a JSON file defining your presentation structure (see `example_presentation.json`)
2. Run the generator:

```bash
python ppt_generator.py --json example_presentation.json --output my_presentation.pptx
```

#### Method 2: Use the Python Class Directly

```python
from ppt_generator import PPTGenerator

# Create a new presentation
ppt = PPTGenerator()

# Add a title slide
ppt.create_title_slide(
    title="My Presentation",
    subtitle="An awesome presentation",
    author="John Doe"
)

# Add content slides
ppt.create_content_slide(
    title="Key Points",
    content_type="bullet",
    content=[
        "First important point",
        "Second important point",
        "Third important point"
    ]
)

# Save the presentation
ppt.save_presentation("my_custom_presentation.pptx")
```

## Slide Types

### 1. Title Slide
Creates a presentation title slide with title, subtitle, and author information.

### 2. Content Slide (Bullet Points)
- Perfect for lists and key points
- Supports multiple bullet points
- Clean, readable formatting

### 3. Content Slide (Text)
- For longer text content
- Ideal for descriptions and explanations

### 4. Two-Column Slide
- Compare two sets of information
- Great for pros/cons, before/after, etc.

### 5. Section Slide
- Divider slides for organizing content
- Helps structure longer presentations

### 6. Image Slide
- Display images with captions
- Automatic image resizing
- Fallback text if image not found

## JSON Configuration Format

```json
{
  "title_slide": {
    "title": "Your Presentation Title",
    "subtitle": "Optional subtitle",
    "author": "Your Name"
  },
  "slides": [
    {
      "type": "section",
      "title": "Section Name"
    },
    {
      "type": "bullet",
      "title": "Slide Title",
      "content": ["Point 1", "Point 2", "Point 3"]
    },
    {
      "type": "text",
      "title": "Slide Title",
      "content": "Your text content here..."
    },
    {
      "type": "two_column",
      "title": "Comparison",
      "left_content": ["Left item 1", "Left item 2"],
      "right_content": ["Right item 1", "Right item 2"]
    },
    {
      "type": "image",
      "title": "Image Slide",
      "image_path": "path/to/image.jpg",
      "caption": "Optional image caption"
    }
  ]
}
```

## Command Line Options

- `--json`, `-j`: Specify a JSON configuration file
- `--output`, `-o`: Set the output filename (default: presentation.pptx)
- `--sample`, `-s`: Create a sample presentation
- `--help`, `-h`: Show help information

## Examples

### Create a business presentation
```bash
python ppt_generator.py --json business_presentation.json --output quarterly_report.pptx
```

### Generate a sample to see all features
```bash
python ppt_generator.py --sample --output sample_demo.pptx
```

### Use in a script
```python
from ppt_generator import PPTGenerator, create_sample_presentation

# Create and save a sample presentation
ppt = create_sample_presentation()
ppt.save_presentation("my_presentation.pptx")
```

## Customization

You can easily extend the `PPTGenerator` class to add new slide types or modify existing ones:

```python
class MyCustomPPTGenerator(PPTGenerator):
    def create_chart_slide(self, title, chart_data):
        # Your custom chart slide implementation
        pass
```

## Requirements

- Python 3.6+
- python-pptx library

## Output

The generated presentations are saved as `.pptx` files that can be opened in:
- Microsoft PowerPoint
- Google Slides
- LibreOffice Impress
- Apple Keynote
- Any other presentation software that supports the PowerPoint format

## Tips

1. **Images**: Place image files in the same directory as your script or use absolute paths
2. **Content Length**: Keep bullet points concise for better readability
3. **JSON Validation**: Validate your JSON files before running to avoid errors
4. **Batch Processing**: You can create multiple presentations by looping through different JSON files

## Troubleshooting

**Issue**: Module not found error
**Solution**: Make sure you've installed the requirements: `pip install -r requirements.txt`

**Issue**: Image not displaying
**Solution**: Check that the image path is correct and the file exists

**Issue**: JSON parsing error
**Solution**: Validate your JSON syntax using an online JSON validator

## License

This project is open source and available under the MIT License.