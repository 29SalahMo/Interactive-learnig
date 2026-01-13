"""
Database Viewer for Child Learning System
Interactive tool to view and understand the database structure and data
"""
import sqlite3
import os
from database import ChildDatabase
from datetime import datetime

def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)

def view_database_structure(db_path="children.db"):
    """Display the database structure (tables and their schemas)"""
    print_separator()
    print("DATABASE STRUCTURE")
    print_separator()
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        print("The database will be created when you first add a child.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in database.")
            conn.close()
            return
        
        print(f"\n📊 Found {len(tables)} table(s):\n")
        
        for table_name in tables:
            table_name = table_name[0]
            print(f"📋 Table: {table_name}")
            print("-" * 70)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"{'Column Name':<20} {'Type':<15} {'Nullable':<10} {'Default':<15}")
            print("-" * 70)
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                nullable = "NO" if not_null else "YES"
                default_str = str(default_val) if default_val else "None"
                pk_marker = " (PRIMARY KEY)" if is_pk else ""
                print(f"{col_name:<20} {col_type:<15} {nullable:<10} {default_str:<15}{pk_marker}")
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print("\n🔗 Foreign Keys:")
                for fk in foreign_keys:
                    print(f"   → {fk[3]} references {fk[2]}.{fk[4]}")
            
            print("\n")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error viewing database structure: {e}")

def view_all_children():
    """Display all children in the database"""
    print_separator()
    print("ALL CHILDREN IN DATABASE")
    print_separator()
    
    try:
        db = ChildDatabase()
        children = db.get_all_children()
        
        if not children:
            print("📭 No children registered in the database yet.")
            return
        
        print(f"\n👥 Found {len(children)} child(ren):\n")
        
        for i, child in enumerate(children, 1):
            gender_emoji = "👧" if child['gender'].lower() == 'girl' else "👦"
            print(f"{i}. {gender_emoji} {child['name']} ({child['gender']})")
            print(f"   ID: {child['id']}")
            print(f"   Created: {child['created_at']}")
            print(f"   Last Login: {child['last_login'] or 'Never'}")
            print(f"   Total Quizzes: {child['total_quizzes']}")
            print(f"   Total Score: {child['total_score']}")
            
            # Calculate average if quizzes exist
            if child['total_quizzes'] > 0:
                avg_score = child['total_score'] / child['total_quizzes']
                print(f"   Average Score: {avg_score:.2f}")
            
            print()
        
    except Exception as e:
        print(f"❌ Error viewing children: {e}")

def view_child_details(name: str):
    """Display detailed information about a specific child"""
    print_separator()
    print(f"CHILD DETAILS: {name}")
    print_separator()
    
    try:
        db = ChildDatabase()
        child = db.get_child_by_name(name)
        
        if not child:
            print(f"❌ Child '{name}' not found in database.")
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
        
        # Check if face encoding exists
        if 'face_encoding' in child and child['face_encoding'] is not None:
            encoding_size = len(child['face_encoding']) if hasattr(child['face_encoding'], '__len__') else 'N/A'
            print(f"\n👤 Face Encoding: Present (Size: {encoding_size})")
        else:
            print(f"\n👤 Face Encoding: Not found")
        
    except Exception as e:
        print(f"❌ Error viewing child details: {e}")

def view_quiz_results(child_name: str = None):
    """Display quiz results"""
    print_separator()
    if child_name:
        print(f"QUIZ RESULTS FOR: {child_name}")
    else:
        print("ALL QUIZ RESULTS")
    print_separator()
    
    try:
        conn = sqlite3.connect("children.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if child_name:
            # Get results for specific child
            cursor.execute("""
                SELECT qr.id, qr.quiz_date, qr.score, qr.total_questions,
                       (qr.score * 100.0 / qr.total_questions) as percentage,
                       c.name
                FROM quiz_results qr
                JOIN children c ON qr.child_id = c.id
                WHERE c.name = ?
                ORDER BY qr.quiz_date DESC
            """, (child_name,))
        else:
            # Get all results
            cursor.execute("""
                SELECT qr.id, qr.quiz_date, qr.score, qr.total_questions,
                       (qr.score * 100.0 / qr.total_questions) as percentage,
                       c.name
                FROM quiz_results qr
                JOIN children c ON qr.child_id = c.id
                ORDER BY qr.quiz_date DESC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            if child_name:
                print(f"📭 No quiz results found for {child_name}.")
            else:
                print("📭 No quiz results in database yet.")
            return
        
        print(f"\n📝 Found {len(results)} quiz result(s):\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - {result['quiz_date']}")
            print(f"   Score: {result['score']}/{result['total_questions']} ({result['percentage']:.1f}%)")
            print()
        
    except Exception as e:
        print(f"❌ Error viewing quiz results: {e}")

def view_database_summary():
    """Display a summary of the database"""
    print_separator()
    print("DATABASE SUMMARY")
    print_separator()
    
    try:
        conn = sqlite3.connect("children.db")
        cursor = conn.cursor()
        
        # Count children
        cursor.execute("SELECT COUNT(*) FROM children")
        num_children = cursor.fetchone()[0]
        
        # Count quiz results
        cursor.execute("SELECT COUNT(*) FROM quiz_results")
        num_results = cursor.fetchone()[0]
        
        # Count face encodings
        cursor.execute("SELECT COUNT(*) FROM face_encodings")
        num_encodings = cursor.fetchone()[0]
        
        # Get total quizzes taken
        cursor.execute("SELECT SUM(total_quizzes) FROM children")
        total_quizzes = cursor.fetchone()[0] or 0
        
        # Get total score
        cursor.execute("SELECT SUM(total_score) FROM children")
        total_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        print(f"\n📊 Database Statistics:")
        print(f"   👥 Total Children: {num_children}")
        print(f"   📝 Total Quiz Results: {num_results}")
        print(f"   👤 Face Encodings: {num_encodings}")
        print(f"   🎯 Total Quizzes Taken: {total_quizzes}")
        print(f"   ⭐ Total Score: {total_score}")
        
        if total_quizzes > 0:
            avg_score = total_score / total_quizzes
            print(f"   📈 Average Score: {avg_score:.2f}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error viewing database summary: {e}")

def interactive_menu():
    """Display interactive menu"""
    while True:
        print_separator()
        print("DATABASE VIEWER - Interactive Menu")
        print_separator()
        print("1. View Database Structure (tables and schemas)")
        print("2. View Database Summary (statistics)")
        print("3. View All Children")
        print("4. View Child Details (by name)")
        print("5. View Quiz Results (all)")
        print("6. View Quiz Results (by child name)")
        print("7. Exit")
        print_separator()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            view_database_structure()
        elif choice == "2":
            view_database_summary()
        elif choice == "3":
            view_all_children()
        elif choice == "4":
            name = input("Enter child's name: ").strip()
            if name:
                view_child_details(name)
        elif choice == "5":
            view_quiz_results()
        elif choice == "6":
            name = input("Enter child's name: ").strip()
            if name:
                view_quiz_results(name)
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print(" " * 15 + "DATABASE VIEWER")
    print(" " * 10 + "Child Learning System Database Explorer")
    print("=" * 70)
    
    # Show database structure first
    view_database_structure()
    
    # Show summary
    view_database_summary()
    
    # Show all children
    view_all_children()
    
    # Start interactive menu
    print("\n")
    interactive_menu()

if __name__ == "__main__":
    main()
