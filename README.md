# My-Moltbot
Ai
#!/usr/bin/env python3
import re
import numpy as np

print("🤖 Moltbot Scientific Analyzer")
print("="*50)

while True:
    cmd = input("\n🔍 Command (or 'quit'): ")
    if cmd.lower() in ['quit', 'exit']: break
    
    # Simple parsing
    if 'Expected' in cmd and 'Actual' in cmd:
        nums = re.findall(r'\d+\.?\d*', cmd)
        if len(nums) >= 10:
            expected = list(map(float, nums[:5]))
            actual = list(map(float, nums[5:10]))
            errors = [a-e for e,a in zip(expected, actual)]
            print(f"\n📊 Errors: {errors}")
            print(f"📈 Max error: {max(errors):.2f}mm")
            print("✅ Analysis complete!")