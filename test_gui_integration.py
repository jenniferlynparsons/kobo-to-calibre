"""
Test GUI integration without actually launching the interface
"""

import sys
sys.path.append('./src')

from config_manager import ConfigManager
from gui import KoboSyncGUI

def test_gui_components():
    print('=== Testing GUI Integration ===')
    
    try:
        # Test configuration loading
        config_manager = ConfigManager()
        print('✓ Configuration manager initialized')
        
        # Test GUI initialization (without running mainloop)
        print('✓ Testing GUI component initialization...')
        
        # This will create the GUI components but not show them
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = KoboSyncGUI(config_manager)
        print('✓ GUI components created successfully')
        
        # Test that all required attributes exist
        assert hasattr(app, 'sync_engine')
        assert hasattr(app, 'notebook')
        assert hasattr(app, 'sync_btn')
        assert hasattr(app, 'discover_btn')
        print('✓ All GUI components properly initialized')
        
        root.destroy()
        print('✓ GUI cleanup successful')
        
        print('\\n🎉 All GUI integration tests passed!')
        print('The application is ready for full testing.')
        
    except Exception as e:
        print(f'❌ GUI test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_gui_components()