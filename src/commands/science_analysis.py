# File: src/commands/science_analysis.py
import numpy as np
import re

class ScienceAnalysisCommand:
    def __init__(self):
        self.expected = [0, 25, 50, 75, 100]
    
    def parse_one_line_command(self, command_text):
        """Parse: 'ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,...] mm'"""
        
        # Extract actual measurements
        match = re.search(r'Actual\s*\[([\d\.,\s]+)\]', command_text)
        if not match:
            raise ValueError("Could not parse actual measurements")
        
        actual_str = match.group(1)
        actual = [float(x.strip()) for x in actual_str.split(',')]
        
        # Extract precision if provided
        precision_match = re.search(r'±([\d\.]+)mm', command_text)
        precision = float(precision_match.group(1)) if precision_match else 0.2
        
        return {
            'expected': self.expected,
            'actual': actual,
            'precision': precision,
            'command': command_text
        }
    
    def execute(self, command_text):
        """Execute the one-line analysis command"""
        parsed = self.parse_one_line_command(command_text)
        
        # Run all analyses
        results = {
            'errors': self.calculate_errors(parsed['expected'], parsed['actual']),
            'z_scores': self.calculate_z_scores(parsed['expected'], parsed['actual'], parsed['precision']),
            'pattern': self.detect_pattern(parsed['actual']),
            'recommendation': self.generate_recommendation(parsed)
        }
        
        return self.format_report(results)
    
    # ... [all the analysis methods from EnhancedDifferenceEngine] ...

# Add to your main command registry:
def setup(bot):
    bot.add_command(ScienceAnalysisCommand())