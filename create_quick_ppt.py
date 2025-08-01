#!/usr/bin/env python3
"""
Quick PPT Creation Example
A simple example showing how to use PPTGenerator class directly.
"""

from ppt_generator import PPTGenerator

def create_quick_presentation():
    """Create a quick presentation example"""
    ppt = PPTGenerator()
    
    # Title slide
    ppt.create_title_slide(
        title="Quick Project Update",
        subtitle="Weekly Status Report",
        author="Project Manager"
    )
    
    # Status section
    ppt.create_section_slide("Project Status")
    
    # Progress slide
    ppt.create_content_slide(
        title="This Week's Accomplishments",
        content_type="bullet",
        content=[
            "Completed user interface design review",
            "Fixed 15 critical bugs in the payment system",
            "Deployed version 2.1 to staging environment",
            "Conducted user acceptance testing with 3 clients",
            "Updated project documentation"
        ]
    )
    
    # Challenges and solutions
    ppt.create_two_column_slide(
        title="Challenges & Solutions",
        left_content=[
            "CHALLENGES:",
            "• Database performance issues",
            "• Third-party API changes",
            "• Team member unavailable",
            "• Client feedback delays"
        ],
        right_content=[
            "SOLUTIONS:",
            "• Optimized queries and indexing",
            "• Updated API integration code",
            "• Redistributed workload",
            "• Set up automated reminders"
        ]
    )
    
    # Next week section
    ppt.create_section_slide("Next Week")
    
    # Upcoming tasks
    ppt.create_content_slide(
        title="Upcoming Priorities",
        content_type="bullet",
        content=[
            "Launch version 2.1 to production",
            "Begin development of mobile app features",
            "Schedule security audit with external team",
            "Prepare Q4 budget proposal",
            "Client demo preparation"
        ]
    )
    
    # Risk assessment
    ppt.create_content_slide(
        title="Risk Assessment",
        content_type="text",
        content="Overall project risk remains LOW. The main areas of concern are the "
                "upcoming security audit results and potential delays from client "
                "feedback cycles. Mitigation strategies are in place, including "
                "buffer time in the schedule and backup plans for critical features."
    )
    
    return ppt

if __name__ == "__main__":
    # Create the presentation
    presentation = create_quick_presentation()
    
    # Save it
    filename = presentation.save_presentation("quick_project_update.pptx")
    print(f"✅ Presentation created successfully: {filename}")
    
    # Show file info
    import os
    file_size = os.path.getsize(filename) / 1024
    print(f"📊 File size: {file_size:.1f} KB")
    print(f"📝 Slides: {len(presentation.presentation.slides)}")
    print("\n🎯 Presentation includes:")
    print("   • Title slide with project info")
    print("   • Section dividers for organization")
    print("   • Bullet point slides for accomplishments and priorities")
    print("   • Two-column comparison slide")
    print("   • Text slide for risk assessment")