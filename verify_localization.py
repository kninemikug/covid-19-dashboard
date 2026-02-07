import pandas as pd
import importlib
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from modules.countries import south_korea, usa, japan, europe

def verify_module(module_name, module, df):
    print(f"\nTesting {module_name}...")
    try:
        result = module.process(df)
        if result is None:
            print(f"❌ {module_name}: Returned None")
            return
        
        metrics = result['metrics']
        visualizations = result['visualizations']
        
        print(f"✅ {module_name}: Processed successfully")
        print(f"   - Metrics keys: {list(metrics.keys())}")
        print(f"   - Visualizations keys: {list(visualizations.keys())}")
        
        # Check specific expected keys based on country
        if module_name == 'Japan':
            if 'wave_detection' in visualizations:
                print("   - ✅ Wave detection chart present")
            else:
                print("   - ❌ Wave detection chart MISSING")
                
        if module_name == 'USA':
            if 'wave_detection' in visualizations: # USA should now have wave detection!
                 print("   - ✅ Wave detection chart present (New Feature!)")
            else:
                 print("   - ⚠️ Wave detection chart missing (Expected if removed/not implemented yet, but we implemented it)")

    except Exception as e:
        print(f"❌ {module_name}: Failed with error: {e}")
        import traceback
        traceback.print_exc()

from modules.data_loader import load_data

def main():
    print("Loading data using modules.data_loader...")
    try:
        # load_data handles downloading and merging
        df = load_data()
        
        if df.empty:
            print("❌ Data loading returned empty DataFrame!")
            return

        print(f"Data loaded successfully. Shape: {df.shape}")
        
        verify_module("South Korea", south_korea, df)
        verify_module("USA", usa, df)
        verify_module("Japan", japan, df)
        verify_module("Europe", europe, df)
        
    except Exception as e:
        print(f"Data loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
