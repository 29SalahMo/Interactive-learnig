"""
Database Control/Management Tool for Child Learning System
Full control over database: add, edit, delete, manage data
"""
import sqlite3
import os
from database import ChildDatabase

def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def list_all_children():
    """List all children in database"""
    try:
        db = ChildDatabase()
        children = db.get_all_children()
        
        if not children:
            print("📭 No children in database.")
            return []
        
        print(f"\n👥 Found {len(children)} child(ren):\n")
        for i, child in enumerate(children, 1):
            gender_emoji = "👧" if child['gender'].lower() == 'girl' else "👦"
            print(f"{i}. {gender_emoji} {child['name']} ({child['gender']}) - ID: {child['id']}")
            print(f"   Quizzes: {child['total_quizzes']}, Score: {child['total_score']}")
        
        return children
    except Exception as e:
        print_error(f"Error listing children: {e}")
        return []

def delete_child_interactive():
    """Interactive function to delete a child"""
    print_separator()
    print("DELETE CHILD")
    print_separator()
    
    children = list_all_children()
    if not children:
        return
    
    print("\nEnter child name to delete (or 'cancel' to go back):")
    name = input("> ").strip()
    
    if name.lower() == 'cancel':
        return
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will delete:")
    print(f"   - Child: {name}")
    print(f"   - Face encoding")
    print(f"   - ALL quiz results for this child")
    print(f"\nThis action CANNOT be undone!")
    
    confirm = input("\nType 'DELETE' to confirm: ").strip()
    if confirm != 'DELETE':
        print("❌ Deletion cancelled.")
        return
    
    try:
        db = ChildDatabase()
        if db.delete_child(name):
            print_success(f"Child '{name}' and all related data deleted successfully!")
        else:
            print_error(f"Child '{name}' not found or deletion failed.")
    except Exception as e:
        print_error(f"Error deleting child: {e}")

def update_child_name_interactive():
    """Interactive function to update a child's name"""
    print_separator()
    print("UPDATE CHILD NAME")
    print_separator()
    
    children = list_all_children()
    if not children:
        return
    
    print("\nEnter current child name:")
    old_name = input("> ").strip()
    
    if not old_name:
        print_error("Name cannot be empty.")
        return
    
    print("\nEnter new name:")
    new_name = input("> ").strip()
    
    if not new_name:
        print_error("New name cannot be empty.")
        return
    
    if old_name == new_name:
        print_warning("Old and new names are the same. No change needed.")
        return
    
    try:
        db = ChildDatabase()
        if db.update_child_name(old_name, new_name):
            print_success(f"Child name updated from '{old_name}' to '{new_name}'!")
        else:
            print_error(f"Failed to update name. Child '{old_name}' may not exist, or '{new_name}' already exists.")
    except Exception as e:
        print_error(f"Error updating child name: {e}")

def view_quiz_results_interactive():
    """Interactive function to view quiz results"""
    print_separator()
    print("VIEW QUIZ RESULTS")
    print_separator()
    
    print("\nView results for:")
    print("1. All children")
    print("2. Specific child")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    try:
        db = ChildDatabase()
        
        if choice == "1":
            results = db.get_quiz_results()
            child_name = None
        elif choice == "2":
            name = input("Enter child name: ").strip()
            if not name:
                print_error("Name cannot be empty.")
                return
            results = db.get_quiz_results(name)
            child_name = name
        else:
            print_error("Invalid choice.")
            return
        
        if not results:
            if child_name:
                print(f"📭 No quiz results found for {child_name}.")
            else:
                print("📭 No quiz results in database.")
            return
        
        print(f"\n📝 Found {len(results)} quiz result(s):\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['child_name']} - {result['quiz_date']}")
            print(f"   Score: {result['score']}/{result['total_questions']} ({result['percentage']}%)")
            print(f"   Result ID: {result['id']}")
            print()
    
    except Exception as e:
        print_error(f"Error viewing quiz results: {e}")

def delete_quiz_result_interactive():
    """Interactive function to delete a quiz result"""
    print_separator()
    print("DELETE QUIZ RESULT")
    print_separator()
    
    try:
        db = ChildDatabase()
        
        # Show all results
        results = db.get_quiz_results()
        if not results:
            print("📭 No quiz results in database.")
            return
        
        print(f"\n📝 Quiz Results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['child_name']} - {result['quiz_date']}")
            print(f"   Score: {result['score']}/{result['total_questions']} ({result['percentage']}%)")
            print(f"   Result ID: {result['id']}")
            print()
        
        result_id = input("Enter Result ID to delete (or 'cancel'): ").strip()
        
        if result_id.lower() == 'cancel':
            return
        
        try:
            result_id = int(result_id)
        except ValueError:
            print_error("Invalid result ID.")
            return
        
        # Confirm
        result_to_delete = next((r for r in results if r['id'] == result_id), None)
        if not result_to_delete:
            print_error(f"Result ID {result_id} not found.")
            return
        
        print(f"\n⚠️  Delete quiz result for {result_to_delete['child_name']}?")
        print(f"   Date: {result_to_delete['quiz_date']}")
        print(f"   Score: {result_to_delete['score']}/{result_to_delete['total_questions']}")
        
        confirm = input("\nType 'DELETE' to confirm: ").strip()
        if confirm != 'DELETE':
            print("❌ Deletion cancelled.")
            return
        
        if db.delete_quiz_result(result_id):
            print_success(f"Quiz result deleted! Child statistics updated.")
        else:
            print_error("Failed to delete quiz result.")
    
    except Exception as e:
        print_error(f"Error deleting quiz result: {e}")

def clear_child_quiz_results_interactive():
    """Interactive function to clear all quiz results for a child"""
    print_separator()
    print("CLEAR ALL QUIZ RESULTS FOR CHILD")
    print_separator()
    
    children = list_all_children()
    if not children:
        return
    
    print("\nEnter child name:")
    name = input("> ").strip()
    
    if not name:
        print_error("Name cannot be empty.")
        return
    
    # Get child info
    try:
        db = ChildDatabase()
        child = db.get_child_by_name(name)
        if not child:
            print_error(f"Child '{name}' not found.")
            return
        
        print(f"\n⚠️  WARNING: This will delete ALL quiz results for {name}")
        print(f"   Current quizzes: {child['total_quizzes']}")
        print(f"   Current total score: {child['total_score']}")
        print(f"\nThis action CANNOT be undone!")
        
        confirm = input("\nType 'CLEAR' to confirm: ").strip()
        if confirm != 'CLEAR':
            print("❌ Operation cancelled.")
            return
        
        if db.clear_child_quiz_results(name):
            print_success(f"All quiz results for '{name}' cleared! Statistics reset.")
        else:
            print_error("Failed to clear quiz results.")
    
    except Exception as e:
        print_error(f"Error clearing quiz results: {e}")

def reset_database_interactive():
    """Interactive function to reset entire database"""
    print_separator()
    print("⚠️  RESET ENTIRE DATABASE ⚠️")
    print_separator()
    
    try:
        db = ChildDatabase()
        
        # Get statistics
        children = db.get_all_children()
        results = db.get_quiz_results()
        
        print(f"\n⚠️  WARNING: This will DELETE ALL DATA:")
        print(f"   - {len(children)} child(ren)")
        print(f"   - {len(results)} quiz result(s)")
        print(f"   - All face encodings")
        print(f"\n⚠️  THIS ACTION CANNOT BE UNDONE!")
        print(f"\n⚠️  Type 'RESET ALL DATA' to confirm:")
        
        confirm = input("> ").strip()
        if confirm != 'RESET ALL DATA':
            print("❌ Reset cancelled.")
            return
        
        if db.reset_database():
            print_success("Database reset successfully! All data deleted.")
        else:
            print_error("Failed to reset database.")
    
    except Exception as e:
        print_error(f"Error resetting database: {e}")

def view_child_details_interactive():
    """Interactive function to view child details"""
    print_separator()
    print("VIEW CHILD DETAILS")
    print_separator()
    
    children = list_all_children()
    if not children:
        return
    
    print("\nEnter child name:")
    name = input("> ").strip()
    
    if not name:
        print_error("Name cannot be empty.")
        return
    
    try:
        db = ChildDatabase()
        child = db.get_child_by_name(name)
        
        if not child:
            print_error(f"Child '{name}' not found.")
            return
        
        gender_emoji = "👧" if child['gender'].lower() == 'girl' else "👦"
        print(f"\n{gender_emoji} {child['name']} ({child['gender']})")
        print(f"ID: {child['id']}")
        print(f"Created: {child['created_at']}")
        print(f"Last Login: {child['last_login'] or 'Never'}")
        print(f"Total Quizzes: {child['total_quizzes']}")
        print(f"Total Score: {child['total_score']}")
        
        if child['total_quizzes'] > 0:
            avg_score = child['total_score'] / child['total_quizzes']
            print(f"Average Score: {avg_score:.2f}")
        
        # Get statistics
        stats = db.get_child_stats(name)
        if stats:
            print(f"\n📊 Statistics:")
            print(f"   Number of Quiz Results: {stats['num_results']}")
            if stats['avg_percentage'] > 0:
                print(f"   Average Percentage: {stats['avg_percentage']}%")
        
        # Show quiz results
        results = db.get_quiz_results(name)
        if results:
            print(f"\n📝 Recent Quiz Results:")
            for result in results[:5]:  # Show last 5
                print(f"   {result['quiz_date']}: {result['score']}/{result['total_questions']} ({result['percentage']}%)")
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more")
        
        # Check face encoding
        if 'face_encoding' in child and child['face_encoding'] is not None:
            encoding_size = len(child['face_encoding']) if hasattr(child['face_encoding'], '__len__') else 'N/A'
            print(f"\n👤 Face Encoding: Present (Size: {encoding_size})")
        else:
            print(f"\n👤 Face Encoding: Not found")
    
    except Exception as e:
        print_error(f"Error viewing child details: {e}")

def main_menu():
    """Main interactive menu"""
    while True:
        print_separator()
        print("DATABASE CONTROL CENTER")
        print("Child Learning System - Full Database Management")
        print_separator()
        print("1. View All Children")
        print("2. View Child Details")
        print("3. Update Child Name")
        print("4. Delete Child")
        print("5. View Quiz Results")
        print("6. Delete Quiz Result")
        print("7. Clear All Quiz Results for Child")
        print("8. Reset Entire Database (⚠️ DANGER)")
        print("9. Exit")
        print_separator()
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == "1":
            list_all_children()
        elif choice == "2":
            view_child_details_interactive()
        elif choice == "3":
            update_child_name_interactive()
        elif choice == "4":
            delete_child_interactive()
        elif choice == "5":
            view_quiz_results_interactive()
        elif choice == "6":
            delete_quiz_result_interactive()
        elif choice == "7":
            clear_child_quiz_results_interactive()
        elif choice == "8":
            reset_database_interactive()
        elif choice == "9":
            print("\n👋 Goodbye!")
            break
        else:
            print_error("Invalid choice. Please enter 1-9.")
        
        if choice != "9":
            input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print(" " * 15 + "DATABASE CONTROL CENTER")
    print(" " * 10 + "Child Learning System - Full Management")
    print("=" * 70)
    
    # Check if database exists
    if not os.path.exists("children.db"):
        print_warning("Database file 'children.db' not found.")
        print("It will be created when you first add a child through the system.")
        print()
    
    main_menu()

if __name__ == "__main__":
    main()
