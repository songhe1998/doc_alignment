#!/usr/bin/env python3
"""
Demo script showing different usage modes for the Legal Document Alignment system.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and show its output"""
    print(f"🚀 Running: {' '.join(cmd)}")
    print("="*60)
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⏹️  Command interrupted by user")
        return False

def main():
    print("📋 Legal Document Alignment System Demo")
    print("="*60)
    
    while True:
        print("\nChoose a demo mode:")
        print("1. Single Document Alignment (detailed output)")
        print("2. Batch Evaluation - Small (3 pairs)")
        print("3. Batch Evaluation - Medium (8 pairs)")
        print("4. Batch Evaluation - Large (15 pairs)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🔍 Running single document alignment with detailed output...")
            success = run_command([sys.executable, "alignment.py"])
            
        elif choice == "2":
            print("\n⚡ Running small batch evaluation (3 pairs)...")
            success = run_command([sys.executable, "alignment.py", "evaluate", "3"])
            
        elif choice == "3":
            print("\n🔄 Running medium batch evaluation (8 pairs)...")
            success = run_command([sys.executable, "alignment.py", "evaluate", "8"])
            
        elif choice == "4":
            print("\n🚀 Running large batch evaluation (15 pairs)...")
            print("⚠️  Warning: This will take approximately 30-45 minutes!")
            confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
            if confirm == 'y':
                success = run_command([sys.executable, "alignment.py", "evaluate", "15"])
            else:
                print("❌ Large evaluation cancelled.")
                continue
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")
            continue
        
        if not success:
            print("⚠️  Command failed or was interrupted.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()




