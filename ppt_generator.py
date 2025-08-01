#!/usr/bin/env python3
"""
PowerPoint Generator
A simple but powerful tool for creating PowerPoint presentations programmatically.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import argparse
import json
import os
from datetime import datetime


class PPTGenerator:
    def __init__(self):
        self.presentation = Presentation()
        
    def create_title_slide(self, title, subtitle="", author=""):
        """Create a title slide"""
        slide_layout = self.presentation.slide_layouts[0]  # Title slide layout
        slide = self.presentation.slides.add_slide(slide_layout)
        
        # Set title
        title_shape = slide.shapes.title
        title_shape.text = title
        
        # Set subtitle if provided
        if subtitle:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle
            
        # Add author and date at the bottom
        if author:
            left = Inches(1)
            top = Inches(7)
            width = Inches(8)
            height = Inches(0.5)
            
            text_box = slide.shapes.add_textbox(left, top, width, height)
            text_frame = text_box.text_frame
            text_frame.text = f"By: {author} | {datetime.now().strftime('%B %Y')}"
            
            # Style the author text
            paragraph = text_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER
            paragraph.font.size = Pt(12)
            paragraph.font.color.rgb = RGBColor(128, 128, 128)
        
        return slide
    
    def create_content_slide(self, title, content_type="bullet", content=None):
        """Create a content slide with various content types"""
        slide_layout = self.presentation.slide_layouts[1]  # Title and Content layout
        slide = self.presentation.slides.add_slide(slide_layout)
        
        # Set title
        title_shape = slide.shapes.title
        title_shape.text = title
        
        # Add content based on type
        content_placeholder = slide.placeholders[1]
        
        if content_type == "bullet" and content:
            text_frame = content_placeholder.text_frame
            text_frame.clear()  # Clear existing content
            
            for item in content:
                p = text_frame.add_paragraph()
                p.text = item
                p.level = 0
                
        elif content_type == "text" and content:
            content_placeholder.text = content
            
        return slide
    
    def create_two_column_slide(self, title, left_content, right_content):
        """Create a slide with two columns of content"""
        slide_layout = self.presentation.slide_layouts[3]  # Two Content layout
        slide = self.presentation.slides.add_slide(slide_layout)
        
        # Set title
        title_shape = slide.shapes.title
        title_shape.text = title
        
        # Left column
        left_placeholder = slide.placeholders[1]
        if isinstance(left_content, list):
            text_frame = left_placeholder.text_frame
            text_frame.clear()
            for item in left_content:
                p = text_frame.add_paragraph()
                p.text = item
        else:
            left_placeholder.text = left_content
            
        # Right column
        right_placeholder = slide.placeholders[2]
        if isinstance(right_content, list):
            text_frame = right_placeholder.text_frame
            text_frame.clear()
            for item in right_content:
                p = text_frame.add_paragraph()
                p.text = item
        else:
            right_placeholder.text = right_content
            
        return slide
    
    def create_image_slide(self, title, image_path, caption=""):
        """Create a slide with an image"""
        slide_layout = self.presentation.slide_layouts[6]  # Blank layout
        slide = self.presentation.slides.add_slide(slide_layout)
        
        # Add title
        left = Inches(1)
        top = Inches(0.5)
        width = Inches(8)
        height = Inches(1)
        
        title_box = slide.shapes.add_textbox(left, top, width, height)
        title_frame = title_box.text_frame
        title_frame.text = title
        title_paragraph = title_frame.paragraphs[0]
        title_paragraph.font.size = Pt(24)
        title_paragraph.font.bold = True
        title_paragraph.alignment = PP_ALIGN.CENTER
        
        # Add image if file exists
        if os.path.exists(image_path):
            left = Inches(2)
            top = Inches(2)
            slide.shapes.add_picture(image_path, left, top, height=Inches(4))
            
            # Add caption if provided
            if caption:
                left = Inches(1)
                top = Inches(6.5)
                width = Inches(8)
                height = Inches(0.5)
                
                caption_box = slide.shapes.add_textbox(left, top, width, height)
                caption_frame = caption_box.text_frame
                caption_frame.text = caption
                caption_paragraph = caption_frame.paragraphs[0]
                caption_paragraph.alignment = PP_ALIGN.CENTER
                caption_paragraph.font.size = Pt(12)
                caption_paragraph.font.italic = True
        else:
            # Add placeholder text if image doesn't exist
            left = Inches(2)
            top = Inches(3)
            width = Inches(6)
            height = Inches(2)
            
            placeholder_box = slide.shapes.add_textbox(left, top, width, height)
            placeholder_frame = placeholder_box.text_frame
            placeholder_frame.text = f"Image not found: {image_path}"
            placeholder_paragraph = placeholder_frame.paragraphs[0]
            placeholder_paragraph.alignment = PP_ALIGN.CENTER
            placeholder_paragraph.font.size = Pt(16)
            placeholder_paragraph.font.color.rgb = RGBColor(255, 0, 0)
        
        return slide
    
    def create_section_slide(self, section_title):
        """Create a section divider slide"""
        slide_layout = self.presentation.slide_layouts[2]  # Section Header layout
        slide = self.presentation.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        title_shape.text = section_title
        
        return slide
    
    def save_presentation(self, filename):
        """Save the presentation to a file"""
        if not filename.endswith('.pptx'):
            filename += '.pptx'
        
        self.presentation.save(filename)
        return filename


def create_sample_presentation():
    """Create a sample presentation with various slide types"""
    ppt = PPTGenerator()
    
    # Title slide
    ppt.create_title_slide(
        title="Sample PowerPoint Presentation",
        subtitle="Created with Python and python-pptx",
        author="PPT Generator"
    )
    
    # Section slide
    ppt.create_section_slide("Introduction")
    
    # Bullet point slide
    ppt.create_content_slide(
        title="Key Features",
        content_type="bullet",
        content=[
            "Easy to use Python script",
            "Multiple slide layouts supported",
            "Customizable content and styling",
            "Programmatic presentation generation",
            "Export to standard .pptx format"
        ]
    )
    
    # Two column slide
    ppt.create_two_column_slide(
        title="Comparison",
        left_content=[
            "Manual Creation:",
            "• Time consuming",
            "• Repetitive tasks",
            "• Error prone",
            "• Hard to maintain"
        ],
        right_content=[
            "Automated Creation:",
            "• Fast and efficient",
            "• Consistent formatting",
            "• Easily reproducible",
            "• Version controlled"
        ]
    )
    
    # Text slide
    ppt.create_content_slide(
        title="About This Tool",
        content_type="text",
        content="This PowerPoint generator is built using the python-pptx library. "
                "It allows you to create professional presentations programmatically, "
                "making it easy to generate reports, dashboards, and other content "
                "that needs to be updated regularly."
    )
    
    # Section slide
    ppt.create_section_slide("Getting Started")
    
    # Instructions slide
    ppt.create_content_slide(
        title="How to Use",
        content_type="bullet",
        content=[
            "Install dependencies: pip install -r requirements.txt",
            "Run the script: python ppt_generator.py",
            "Customize the create_sample_presentation() function",
            "Or use the PPTGenerator class in your own code",
            "Save and share your .pptx files"
        ]
    )
    
    return ppt


def load_presentation_from_json(json_file):
    """Load presentation structure from a JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    ppt = PPTGenerator()
    
    # Create title slide
    title_info = data.get('title_slide', {})
    ppt.create_title_slide(
        title=title_info.get('title', 'Untitled Presentation'),
        subtitle=title_info.get('subtitle', ''),
        author=title_info.get('author', '')
    )
    
    # Create content slides
    for slide_data in data.get('slides', []):
        slide_type = slide_data.get('type', 'content')
        
        if slide_type == 'section':
            ppt.create_section_slide(slide_data.get('title', 'Section'))
        elif slide_type == 'bullet':
            ppt.create_content_slide(
                title=slide_data.get('title', 'Slide'),
                content_type='bullet',
                content=slide_data.get('content', [])
            )
        elif slide_type == 'text':
            ppt.create_content_slide(
                title=slide_data.get('title', 'Slide'),
                content_type='text',
                content=slide_data.get('content', '')
            )
        elif slide_type == 'two_column':
            ppt.create_two_column_slide(
                title=slide_data.get('title', 'Slide'),
                left_content=slide_data.get('left_content', []),
                right_content=slide_data.get('right_content', [])
            )
        elif slide_type == 'image':
            ppt.create_image_slide(
                title=slide_data.get('title', 'Slide'),
                image_path=slide_data.get('image_path', ''),
                caption=slide_data.get('caption', '')
            )
    
    return ppt


def main():
    parser = argparse.ArgumentParser(description='Generate PowerPoint presentations')
    parser.add_argument('--json', '-j', help='JSON file with presentation structure')
    parser.add_argument('--output', '-o', default='presentation.pptx', 
                       help='Output filename (default: presentation.pptx)')
    parser.add_argument('--sample', '-s', action='store_true',
                       help='Create a sample presentation')
    
    args = parser.parse_args()
    
    if args.json:
        if os.path.exists(args.json):
            ppt = load_presentation_from_json(args.json)
            print(f"Loading presentation from {args.json}")
        else:
            print(f"Error: JSON file {args.json} not found")
            return
    elif args.sample:
        ppt = create_sample_presentation()
        print("Creating sample presentation")
    else:
        ppt = create_sample_presentation()
        print("No input specified, creating sample presentation")
    
    # Save the presentation
    filename = ppt.save_presentation(args.output)
    print(f"Presentation saved as: {filename}")
    print(f"File size: {os.path.getsize(filename) / 1024:.1f} KB")


if __name__ == "__main__":
    main()