from face_auth import FaceAuthManager


def main() -> None:
    """
    Register (sign up) a child using the webcam.
    Run from the project root:
        python face_register.py
    """
    name = input("Enter child name to register: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    
    # Ask for gender
    print("\nPlease select gender:")
    print("1. Boy")
    print("2. Girl")
    choice = input("Enter choice (1 or 2, default is 1): ").strip()
    
    if choice == '2':
        gender = 'girl'
    else:
        gender = 'boy'
    
    print(f"\nRegistering {name} as {gender}...")

    auth = FaceAuthManager(camera_index=0)
    ok = auth.register_child(name, gender)

    if ok:
        print(f"[OK] Registration completed for: {name} ({gender})")
    else:
        print("[ERROR] Registration failed.")


if __name__ == "__main__":
    main()


